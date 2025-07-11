"""
MCP鉴权管理API视图

提供MCP服务鉴权相关的API接口
"""

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import List

from app.services.auth.secret_manager import SecretManager
from app.utils.logging import mcp_logger
from app.utils.response import success_response, error_response
from app.utils.permissions import get_user_info
from app.utils.const import error_code
from app.utils.http.utils import body_page_params


async def create_secret(request: Request) -> JSONResponse:
    """创建服务密钥"""
    try:
        # 获取路径参数
        service_id = int(request.path_params.get('service_id'))

        # 获取请求体
        body = await request.json()
        name = body.get('name', '').strip()
        description = body.get('description', '')
        expires_days = body.get('expires_days', 0)
        limit_count = body.get('limit_count', 0)

        # 验证参数
        if not name:
            return error_response("密钥名称不能为空", status_code=400)

        if len(name) > 100:
            return error_response("密钥名称长度不能超过100字符", status_code=400)

        user_id, is_admin = get_user_info(request)

        # 生成密钥
        secret_info = SecretManager.generate_secret(
            service_id=service_id,
            name=name,
            description=description,
            expires_days=expires_days,
            limit_count=limit_count,
            user_id=user_id
        )

        mcp_logger.info(f"用户 {user_id} 为服务 {service_id} 创建密钥: {name}")

        return success_response(data=secret_info, message="密钥创建成功")

    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        mcp_logger.error(f"创建密钥失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def get_secrets(request: Request) -> JSONResponse:
    """获取服务密钥列表"""
    try:
        service_id = int(request.path_params.get('service_id'))

        # 获取用户信息
        user_id, is_admin = get_user_info(request)
        
        # 如果无法获取用户信息，返回错误
        if user_id is None and not is_admin:
            return error_response("用户未认证", status_code=error_code.UNAUTHORIZED)

        secrets = SecretManager.list_secrets(
            service_id=service_id,
            user_id=user_id,
            is_admin=is_admin
        )

        return success_response(data=secrets, message="获取密钥列表成功")

    except Exception as e:
        mcp_logger.error(f"获取密钥列表失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def update_secret(request: Request) -> JSONResponse:
    """更新密钥信息"""
    try:
        secret_id = int(request.path_params.get('secret_id'))

        # 获取请求体
        body = await request.json()
        name = body.get('name')
        description = body.get('description')
        is_active = body.get('is_active')
        limit_count = body.get('limit_count', 0)

        # 验证参数
        if name is not None and (not name.strip() or len(name) > 100):
            return error_response("密钥名称格式错误", status_code=400)

        # 获取用户信息
        user_id, is_admin = get_user_info(request)

        secret_info = SecretManager.update_secret(
            secret_id=secret_id,
            name=name.strip() if name else None,
            description=description,
            is_active=is_active,
            limit_count=limit_count,
            user_id=user_id,
            is_admin=is_admin
        )

        if not secret_info:
            return error_response("密钥不存在或无权限操作", status_code=404)

        mcp_logger.info(f"用户 {user_id} 更新密钥: {secret_id}")

        return success_response(data=secret_info, message="密钥更新成功")

    except Exception as e:
        mcp_logger.error(f"更新密钥失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def delete_secret(request: Request) -> JSONResponse:
    """删除密钥"""
    try:
        secret_id = int(request.path_params.get('secret_id'))

        # 获取用户信息
        user_id, is_admin = get_user_info(request)

        success = SecretManager.delete_secret(
            secret_id=secret_id,
            user_id=user_id,
            is_admin=is_admin
        )

        if not success:
            return error_response("密钥不存在或无权限操作", status_code=404)

        mcp_logger.info(f"用户 {user_id} 删除密钥: {secret_id}")

        return success_response(message="密钥删除成功")

    except Exception as e:
        mcp_logger.error(f"删除密钥失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def get_secret_statistics(request: Request) -> JSONResponse:
    """获取密钥统计数据"""
    try:
        secret_id = int(request.path_params.get('secret_id'))
        days = int(request.query_params.get('days', 30))

        # 验证参数
        if days < 1 or days > 365:
            return error_response("统计天数必须在1-365之间", status_code=400)

        statistics = SecretManager.get_secret_statistics(
            secret_id=secret_id,
            days=days
        )

        return success_response(
            data=statistics,
            message="获取统计数据成功"
        )

    except Exception as e:
        mcp_logger.error(f"获取密钥统计失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def get_access_logs(request: Request) -> JSONResponse:
    """获取服务访问日志"""
    try:
        service_id = request.path_params.get('service_id')
        data = await request.json()
        # 获取分页参数
        page_params = body_page_params(data)
        condition = data.get('condition', {})
        secret_id = None
        status = None
        date_range = None
        if condition.get('secret_id') is not None:
            secret_id = condition.get('secret_id')
        if condition.get('status') is not None:
            status = condition.get('status')
        if condition.get('date_range') is not None:
            date_range = condition.get('date_range')

        logs, total = SecretManager.get_access_logs(
            service_id=service_id,
            page_params=page_params,
            secret_id=int(secret_id) if secret_id else None,
            status=status,
            date_range=date_range
        )

        return success_response(data=logs, message="获取访问日志成功", total=total)

    except Exception as e:
        mcp_logger.error(f"获取访问日志失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def get_auth_config(request: Request) -> JSONResponse:
    """获取服务鉴权配置"""
    try:
        from app.models.engine import get_db
        from app.models.modules.mcp_services import McpService

        service_id = int(request.path_params.get('service_id'))

        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.id == service_id
            ).first()

            if not service:
                return error_response("服务不存在", status_code=404)

            # 简化权限检查
            # 实际应用中应该检查用户权限

            config = {
                "service_id": service.id,
                "service_name": service.name,
                "auth_required": service.auth_required,
                "auth_mode": service.auth_mode,
                "auth_mode_name": service.get_auth_mode_name(),
                "active_secrets_count": service.get_active_secrets_count()
            }

            return success_response(data=config, message="获取鉴权配置成功")

    except Exception as e:
        mcp_logger.error(f"获取鉴权配置失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def update_auth_config(request: Request) -> JSONResponse:
    """更新服务鉴权配置"""
    try:
        from app.models.engine import get_db
        from app.models.modules.mcp_services import McpService

        service_id = int(request.path_params.get('service_id'))

        # 获取请求体
        body = await request.json()
        auth_required = body.get('auth_required', False)
        auth_mode = body.get('auth_mode', '')

        # 验证鉴权模式
        valid_modes = ["", "secret", "token"]
        if auth_mode not in valid_modes:
            return error_response("无效的鉴权模式", status_code=400)

        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.id == service_id
            ).first()

            if not service:
                return error_response("服务不存在", status_code=404)

            # 简化权限检查
            # 实际应用中应该检查用户权限

            # 更新配置
            service.auth_required = auth_required
            service.auth_mode = auth_mode if auth_required else ""

            db.commit()

            mcp_logger.info(f"更新服务 {service_id} 鉴权配置")

            return success_response(
                data={
                    "service_id": service.id,
                    "auth_required": service.auth_required,
                    "auth_mode": service.auth_mode
                },
                message="鉴权配置更新成功"
            )

    except Exception as e:
        mcp_logger.error(f"更新鉴权配置失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


async def get_secret_info(request: Request) -> JSONResponse:
    """获取密钥信息"""
    try:
        service_id = int(request.path_params.get('service_id'))

        # 获取用户信息
        user_id, is_admin = get_user_info(request)
        
        # 如果无法获取用户信息，返回错误
        if user_id is None and not is_admin:
            return error_response("用户未认证", status_code=error_code.UNAUTHORIZED)

        secret_info = SecretManager.get_secret_info(
            service_id=service_id,
            user_id=user_id,
            is_admin=is_admin
        )

        if secret_info is None:
            return error_response("未找到密钥信息或无权限访问", status_code=error_code.HTTP_NOT_FOUND)

        return success_response(data=secret_info, message="获取密钥信息成功")

    except Exception as e:
        mcp_logger.error(f"获取密钥信息失败: {str(e)}")
        return error_response("服务器内部错误", status_code=500)


def get_router() -> List[Route]:
    """获取MCP鉴权管理路由"""
    return [
        Route("/services/{service_id:int}/secrets",
              create_secret, methods=["POST"]),
        Route("/services/{service_id:int}/secrets",
              get_secrets, methods=["GET"]),
        Route("/secrets/{secret_id:int}", update_secret, methods=["PUT"]),
        Route("/secrets/{secret_id:int}", delete_secret, methods=["DELETE"]),
        Route("/secrets/{secret_id:int}/statistics",
              get_secret_statistics, methods=["GET"]),
        Route("/services/{service_id:int}/secrets-info",
              get_secret_info, methods=["GET"]),
        Route("/services/{service_id:int}/access-logs",
              get_access_logs, methods=["POST"]),
        Route("/services/{service_id:int}/auth-config",
              get_auth_config, methods=["GET"]),
        Route("/services/{service_id:int}/auth-config",
              update_auth_config, methods=["PUT"]),
    ]
