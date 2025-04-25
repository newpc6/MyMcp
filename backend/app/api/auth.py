"""
用户认证和管理API模块
"""
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
import json
from datetime import datetime, timedelta
import jwt as pyjwt  # 重命名以确保使用正确的PyJWT库

from app.services.users import UserService, TenantService
from app.core.config import settings
from app.utils.logging import em_logger
from app.utils.response import success_response, error_response

# JWT密钥
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时


async def login(request: Request):
    """用户登录API"""
    try:
        data = await request.json()
        
        if not data:
            return error_response("无效的请求数据")
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return error_response("用户名和密码不能为空")
        
        # 验证用户
        user = UserService.validate_login(username, password)
        if not user:
            return error_response("用户名或密码错误", code=401, http_status_code=401)
        
        # 生成JWT令牌
        access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "is_admin": user.is_admin,
            "exp": access_token_expires
        }
        token = pyjwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # 获取用户关联的租户
        tenants = TenantService.get_user_tenants(user.id)
        tenant_list = [{"id": t.id, "name": t.name, "code": t.code} for t in tenants]
        
        # 设置Cookie
        response = success_response({
            "user_id": user.id,
            "username": user.username,
            "fullname": user.fullname,
            "is_admin": user.is_admin,
            "tenants": tenant_list,
            "token": token
        }, "登录成功", code=0)
        
        if isinstance(response, tuple):
            # 如果是flask响应对象，转换为starlette格式
            content, status_code = response
            response = Response(
                content=json.dumps(content.json),
                status_code=status_code,
                media_type="application/json"
            )
        
        # 设置Cookie
        cookie_params = {
            "key": "auth_token",
            "value": token,
            "max_age": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "path": "/",
            "httponly": True,
            "samesite": "none"  # 允许跨站请求
        }
        
        # 在生产环境设置安全Cookie
        if settings.ENVIRONMENT == "production" or True:  # 强制启用secure
            cookie_params["secure"] = True
            
        response.set_cookie(**cookie_params)
        
        return response
    
    except Exception as e:
        em_logger.error(f"登录失败: {str(e)}")
        return error_response("登录处理过程中发生错误", code=500, http_status_code=500)


async def logout(request: Request):
    """用户登出API"""
    response = success_response(message="登出成功")
    
    # 清除认证Cookie
    if isinstance(response, tuple):
        # 如果是flask响应对象，转换为starlette格式
        content, status_code = response
        response = Response(
            content=json.dumps(content.json),
            status_code=status_code,
            media_type="application/json"
        )
    
    response.delete_cookie(key="auth_token", path="/")
    
    return response


async def get_current_user(request: Request):
    """获取当前登录用户信息"""
    # 从请求中获取用户信息
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    user_id = request.state.user.get("user_id")
    
    if not user_id:
        return error_response("未登录", code=401, http_status_code=401)
    
    # 获取用户信息
    user = UserService.get_user_by_id(user_id)
    if not user:
        return error_response("用户不存在", code=401, http_status_code=401)
    
    # 获取用户关联的租户
    tenants = TenantService.get_user_tenants(user.id)
    tenant_list = [{"id": t.id, "name": t.name, "code": t.code} for t in tenants]
    
    return success_response({
        "user_id": user.id,
        "username": user.username,
        "fullname": user.fullname,
        "email": user.email,
        "is_admin": user.is_admin,
        "status": user.status,
        "tenants": tenant_list
    })


async def get_users(request: Request):
    """获取所有用户（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    users = UserService.get_all_users()
    
    user_list = []
    for user in users:
        # 获取用户关联的租户
        tenants = TenantService.get_user_tenants(user.id)
        tenant_list = [{"id": t.id, "name": t.name, "code": t.code} for t in tenants]
        
        user_list.append({
            "id": user.id,
            "username": user.username,
            "fullname": user.fullname,
            "email": user.email,
            "is_admin": user.is_admin,
            "status": user.status,
            "tenants": tenant_list,
            "created_at": (user.created_at.strftime("%Y-%m-%d %H:%M:%S") 
                          if user.created_at else None)
        })
    
    return success_response(user_list)


async def create_user(request: Request):
    """创建新用户（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        data = await request.json()
        
        if not data:
            return error_response("无效的请求数据")
        
        username = data.get('username')
        password = data.get('password')
        fullname = data.get('fullname')
        email = data.get('email')
        is_admin = data.get('is_admin', False)
        tenant_ids = data.get('tenant_ids', [])
        
        if not username or not password:
            return error_response("用户名和密码不能为空")
        
        # 创建用户
        user = UserService.create_user(
            username=username,
            password=password,
            fullname=fullname,
            email=email,
            is_admin=is_admin,
            tenant_ids=tenant_ids
        )
        
        if not user:
            return error_response("创建用户失败，可能用户名已存在")
        
        # 获取用户关联的租户
        tenants = TenantService.get_user_tenants(user.id)
        tenant_list = [{"id": t.id, "name": t.name, "code": t.code} for t in tenants]
        
        return success_response({
            "id": user.id,
            "username": user.username,
            "fullname": user.fullname,
            "email": user.email,
            "is_admin": user.is_admin,
            "status": user.status,
            "tenants": tenant_list
        }, "创建用户成功")
        
    except Exception as e:
        em_logger.error(f"创建用户失败: {str(e)}")
        return error_response("处理请求时发生错误", code=500, http_status_code=500)


async def update_user(request: Request):
    """更新用户信息（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        # 获取用户ID
        user_id = int(request.path_params["user_id"])
        data = await request.json()
        
        if not data:
            return error_response("无效的请求数据")
        
        username = data.get('username')
        fullname = data.get('fullname')
        email = data.get('email')
        password = data.get('password')
        is_admin_val = data.get('is_admin')
        status = data.get('status')
        tenant_ids = data.get('tenant_ids')
        
        # 更新用户基本信息
        result = UserService.update_user(
            user_id=user_id,
            username=username,
            fullname=fullname,
            email=email,
            password=password,
            is_admin=is_admin_val,
            status=status
        )
        
        if not result:
            return error_response("更新用户信息失败")
        
        # 如果提供了租户ID列表，更新用户租户关联
        if tenant_ids is not None:
            tenant_result = UserService.update_user_tenants(
                user_id, tenant_ids
            )
            if not tenant_result:
                return error_response("更新用户租户关联失败")
        
        # 获取更新后的用户信息
        user = UserService.get_user_by_id(user_id)
        if not user:
            return error_response("获取用户信息失败", code=404, http_status_code=404)
        
        # 获取用户关联的租户
        tenants = TenantService.get_user_tenants(user.id)
        tenant_list = [{"id": t.id, "name": t.name, "code": t.code} for t in tenants]
        
        return success_response({
            "id": user.id,
            "username": user.username,
            "fullname": user.fullname,
            "email": user.email,
            "is_admin": user.is_admin,
            "status": user.status,
            "tenants": tenant_list
        }, "更新用户成功")
        
    except ValueError:
        return error_response("无效的用户ID", code=400, http_status_code=400)
    except Exception as e:
        em_logger.error(f"更新用户失败: {str(e)}")
        return error_response("处理请求时发生错误", code=500, http_status_code=500)


async def delete_user(request: Request):
    """删除用户（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        # 获取用户ID
        user_id = int(request.path_params["user_id"])
        
        # 不允许删除当前登录用户
        current_user_id = request.state.user.get("user_id")
        if user_id == current_user_id:
            return error_response("不能删除当前登录的用户")
        
        result = UserService.delete_user(user_id)
        if not result:
            return error_response("删除用户失败")
        
        return success_response(message="删除用户成功")
        
    except ValueError:
        return error_response("无效的用户ID", code=400, http_status_code=400)
    except Exception as e:
        em_logger.error(f"删除用户失败: {str(e)}")
        return error_response("处理请求时发生错误", code=500, http_status_code=500)


async def change_password(request: Request):
    """修改当前用户密码"""
    # 获取当前用户ID
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    user_id = request.state.user.get("user_id")
    if not user_id:
        return error_response("未登录", code=401, http_status_code=401)
    
    try:
        data = await request.json()
        
        if not data:
            return error_response("无效的请求数据")
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return error_response("旧密码和新密码不能为空")
        
        # 验证旧密码
        user = UserService.get_user_by_id(user_id)
        if not user:
            return error_response("用户不存在", code=401, http_status_code=401)
        
        if not user.check_password(old_password):
            return error_response("旧密码不正确")
        
        # 更新密码
        result = UserService.update_user(
            user_id=user_id,
            password=new_password
        )
        
        if not result:
            return error_response("修改密码失败")
        
        return success_response(message="密码修改成功")
        
    except Exception as e:
        em_logger.error(f"修改密码失败: {str(e)}")
        return error_response("处理请求时发生错误", code=500, http_status_code=500)


# ============= 租户管理 =============

async def get_tenants(request: Request):
    """获取所有租户（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    tenants = TenantService.get_all_tenants()
    
    tenant_list = []
    for tenant in tenants:
        tenant_list.append({
            "id": tenant.id,
            "name": tenant.name,
            "code": tenant.code,
            "description": tenant.description,
            "status": tenant.status,
            "created_at": (tenant.created_at.strftime("%Y-%m-%d %H:%M:%S") 
                          if tenant.created_at else None)
        })
    
    return success_response(tenant_list)


async def create_tenant(request: Request):
    """创建新租户（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        data = await request.json()
        
        if not data:
            return error_response("无效的请求数据")
        
        name = data.get('name')
        code = data.get('code')
        description = data.get('description')
        
        if not name or not code:
            return error_response("租户名称和代码不能为空")
        
        # 创建租户
        tenant = TenantService.create_tenant(
            name=name,
            code=code,
            description=description
        )
        
        if not tenant:
            return error_response("创建租户失败，可能代码已存在")
        
        return success_response({
            "id": tenant.id,
            "name": tenant.name,
            "code": tenant.code,
            "description": tenant.description,
            "status": tenant.status
        }, "创建租户成功")
        
    except Exception as e:
        em_logger.error(f"创建租户失败: {str(e)}")
        return error_response("处理请求时发生错误", code=500, http_status_code=500)


async def update_tenant(request: Request):
    """更新租户信息（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        # 获取租户ID
        tenant_id = int(request.path_params["tenant_id"])
        data = await request.json()
        
        if not data:
            return error_response("无效的请求数据")
        
        name = data.get('name')
        description = data.get('description')
        status = data.get('status')
        
        # 更新租户信息
        result = TenantService.update_tenant(
            tenant_id=tenant_id,
            name=name,
            description=description,
            status=status
        )
        
        if not result:
            return error_response("更新租户信息失败")
        
        # 获取更新后的租户信息
        tenant = TenantService.get_tenant_by_id(tenant_id)
        if not tenant:
            return error_response("获取租户信息失败", code=404, http_status_code=404)
        
        return success_response({
            "id": tenant.id,
            "name": tenant.name,
            "code": tenant.code,
            "description": tenant.description,
            "status": tenant.status
        }, "更新租户成功")
        
    except ValueError:
        return error_response("无效的租户ID", code=400, http_status_code=400)
    except Exception as e:
        em_logger.error(f"更新租户失败: {str(e)}")
        return error_response("处理请求时发生错误", code=500, http_status_code=500)


async def delete_tenant(request: Request):
    """删除租户（仅管理员）"""
    # 检查管理员权限
    if not hasattr(request.state, 'user'):
        return error_response("未登录", code=401, http_status_code=401)
    
    is_admin = request.state.user.get("is_admin", False)
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        # 获取租户ID
        tenant_id = int(request.path_params["tenant_id"])
        
        result = TenantService.delete_tenant(tenant_id)
        if not result:
            return error_response("删除租户失败")
        
        return success_response(message="删除租户成功")
        
    except ValueError:
        return error_response("无效的租户ID", code=400, http_status_code=400)
    except Exception as e:
        em_logger.error(f"删除租户失败: {str(e)}")
        return error_response("处理请求时发生错误", code=500, http_status_code=500)


# JWT验证中间件已被AuthMiddleware替代，不再需要
# async def auth_middleware(request: Request, call_next):
#     """认证中间件，验证用户身份并设置scope信息"""
#     # 该功能已由app/middleware/auth.py中的AuthMiddleware实现
#     return await call_next(request)


def get_router():
    """获取所有认证相关路由"""
    routes = [
        Route("/login", login, methods=["POST"]),
        Route("/logout", logout, methods=["POST"]),
        Route("/current-user", get_current_user, methods=["GET"]),
        Route("/users", get_users, methods=["GET"]),
        Route("/users", create_user, methods=["POST"]),
        Route("/users/{user_id:int}", update_user, methods=["PUT"]),
        Route("/users/{user_id:int}", delete_user, methods=["DELETE"]),
        Route("/change-password", change_password, methods=["POST"]),
        Route("/tenants", get_tenants, methods=["GET"]),
        Route("/tenants", create_tenant, methods=["POST"]),
        Route("/tenants/{tenant_id:int}", update_tenant, methods=["PUT"]),
        Route("/tenants/{tenant_id:int}", delete_tenant, methods=["DELETE"]),
    ]
    
    return routes 