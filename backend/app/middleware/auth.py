"""
认证中间件模块

使用Starlette实现的身份验证中间件
"""
from fastapi import Request
import requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.services.users import UserService
from app.utils.response import error_response
from app.utils.logging import em_logger
from app.core.config import settings
from app.utils.cache import memory_cache
# 重命名以确保使用正确的PyJWT库
import jwt as pyjwt
import time
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta


# JWT令牌过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 缓存键前缀
EGOVAKB_TOKEN_CACHE_PREFIX = "egovakb_token:"
USER_TOKEN_CACHE_PREFIX = "user_token:"


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件，验证用户登录状态和权限"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # API相关公开路径
        self.public_api_paths = [
            "/auth/login", 
            "/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        # 前端静态资源路径 - 这些路径完全不需要认证
        self.public_static_paths = [
            "/",
            "/assets/",
            "/vite.svg",
            "/index.html",
            "/favicon.ico"
        ]
        self.sse_paths = [
            "/sse",
            "/messages/"
        ]
        # 添加静态文件扩展名列表
        self.static_extensions = [
            ".js", ".css", ".html", ".htm", ".json", ".png", 
            ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".eot", 
            ".woff", ".woff2", ".ttf", ".otf"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并验证认证
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            响应对象
        """
        path = request.url.path
        em_logger.debug(f"处理请求: {path}")
        
        # 首先检查是否为API路径 - API路径的处理优先级高于静态资源
        if path.startswith("/api"):
            # 如果是API公开路径，直接放行
            if self._is_public_api_path(path):
                return await call_next(request)
                
            # 否则需要验证认证
            return await self._authenticate_api_request(request, call_next)
        
        # 处理静态资源文件 - 完全不需要认证
        if self._is_static_resource(path):
            em_logger.debug(f"允许访问静态资源: {path}")
            return await call_next(request)
        
        # 检查SSE路径
        if self._is_sse_path(path):
            return await call_next(request)
            
        # 其他路径作为前端路由处理，不需要认证
        return await call_next(request)
    
    async def _authenticate_api_request(self, request: Request, call_next):
        """
        验证API请求的认证信息
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            响应对象
        """
        # 获取认证令牌
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return error_response(http_status_code=401, message="未提供认证令牌")
            
        # 提取令牌
        token = auth_header.replace("Bearer ", "")
        if not token:
            return error_response(http_status_code=401, message="无效的认证令牌格式")
            
        # 尝试从缓存获取用户数据
        cache_key = USER_TOKEN_CACHE_PREFIX + token
        cached_user_data = memory_cache.get(cache_key)
        
        if cached_user_data:
            # 使用缓存的用户数据
            user_data = cached_user_data
            is_valid = True
        else:
            # 首先尝试验证JWT令牌
            user_data, is_valid = self._validate_token(token)
            
            if not is_valid:
                # 如果JWT验证失败，尝试验证EGova KB令牌
                user_data = self._validate_egova_kb_token(token)
                is_valid = user_data is not None
                
                if is_valid:
                    # 生成JWT令牌并缓存用户数据
                    jwt_token = self._generate_jwt_token(user_data)
                    # 使用新生成的JWT令牌缓存用户数据
                    memory_cache.set(
                        USER_TOKEN_CACHE_PREFIX + jwt_token,
                        user_data,
                        expire_seconds=ACCESS_TOKEN_EXPIRE_MINUTES * 60
                    )
            
            # 缓存用户数据
            if is_valid:
                memory_cache.set(
                    cache_key, 
                    user_data,
                    expire_seconds=ACCESS_TOKEN_EXPIRE_MINUTES * 60
                )
        
        if not is_valid:
            return error_response(http_status_code=401, message="认证令牌无效或已过期")
            
        # 检查权限
        admin_required = self._requires_admin(request.url.path)
        is_admin = user_data.get("is_admin", False)
        if admin_required and not is_admin:
            return error_response(http_status_code=403, message="需要管理员权限")
            
        # 将用户数据添加到请求中
        request.state.user = user_data
        
        # 继续处理请求
        return await call_next(request)
    
    def _is_public_api_path(self, path: str) -> bool:
        """检查路径是否为公开API路径"""
        return any(
            path.startswith(public_path) or path.endswith(public_path)
            for public_path in self.public_api_paths
        )
    
    def _is_static_resource(self, path: str) -> bool:
        """检查路径是否为静态资源"""
        # 排除API路径
        if path.startswith("/api"):
            return False
            
        # 检查是否为明确的静态资源路径
        if any(path.startswith(static_path) for static_path in self.public_static_paths):
            return True
            
        # 检查是否以资源路径开头
        if path.startswith("/assets/"):
            return True
            
        # 检查文件扩展名
        return self._is_static_file(path)
    
    def _is_sse_path(self, path: str) -> bool:
        """检查是否为SSE路径"""
        return any(
            path.endswith(sse_path)
            for sse_path in self.sse_paths
        )
    
    def _is_static_file(self, path: str) -> bool:
        """检查是否为静态文件（根据扩展名）"""
        return any(path.endswith(ext) for ext in self.static_extensions)
    
    def _requires_admin(self, path: str) -> bool:
        """检查路径是否需要管理员权限"""
        admin_paths = ["/api/users", "/api/tenants", "/api/admin"]
        return any(
            path.startswith(admin_path) 
            for admin_path in admin_paths
        )
    
    def _validate_token(
        self, token: str
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            (用户数据, 是否有效)
        """
        try:
            # 使用PyJWT验证令牌
            payload = pyjwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=["HS256"]
            )
            
            # 检查令牌是否过期
            if "exp" in payload and payload["exp"] < time.time():
                return None, False
            
            # 确保用户数据中包含user_id字段（从sub字段获取）
            if "sub" in payload and "user_id" not in payload:
                payload["user_id"] = payload["sub"]
                
            if "user_id" in payload:
                if isinstance(payload["user_id"], str):
                    payload["user_id"] = int(payload["user_id"])
            
            # 返回用户数据
            return payload, True
        except Exception as e:
            em_logger.error(f"令牌验证失败: {str(e)}")
            return None, False
    
    def _validate_egova_kb_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证EGova KB令牌
        
        Args:
            token: EGova KB令牌
            
        Returns:
            验证成功返回用户数据，否则返回None
        """
        try:
            # 首先从缓存中查找，避免重复调用接口
            cache_key = EGOVAKB_TOKEN_CACHE_PREFIX + token
            cached_user_data = memory_cache.get(cache_key)
            
            if cached_user_data:
                em_logger.debug("使用缓存的EGova KB令牌数据")
                return cached_user_data
            
            # 调用egovakb接口获取用户信息
            url = f"{settings.PLATFORM_EGOVA_KB}/api/callback/auth"
            headers = {
                "Authorization": token,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                url, headers=headers, timeout=10.0
            )
            
            if response.status_code != 200:
                error_msg = f"调用egovakb接口失败: {response.status_code} {response.text}"
                em_logger.error(error_msg)
                return None
            
            data = response.json()
            
            if data.get("code") != 200 or "data" not in data:
                em_logger.error(f"egovakb返回错误: {data}")
                return None
            
            user_data = data["data"]
            external_id = user_data.get("user_id")
            username = user_data.get("username")
            email = user_data.get("email")
            
            if not external_id or not username:
                em_logger.error(f"egovakb返回的用户数据不完整: {user_data}")
                return None
            
            # 检查用户是否已存在(根据外部ID)
            existing_user = UserService.get_user_by_external_id(
                external_id, "egovakb"
            )
            
            if existing_user:
                # 用户已存在，更新email信息
                UserService.update_user(
                    user_id=existing_user.id,
                    email=email
                )
                
                # 构建用户数据
                result_data = {
                    "user_id": existing_user.id,
                    "username": existing_user.username,
                    "fullname": existing_user.fullname,
                    "email": existing_user.email,
                    "is_admin": existing_user.is_admin,
                    "external_id": external_id
                }
            else:
                # 创建新用户
                password = settings.DEFAULT_PASSWORD
                new_user = UserService.create_user(
                    username=username,
                    password=password,
                    email=email,
                    fullname=username,
                    is_admin=False,
                    external_id=external_id,
                    platform_type="egovakb"
                )
                
                if not new_user:
                    em_logger.error(f"创建导入用户失败: {username}")
                    return None
                
                # 构建用户数据
                result_data = {
                    "user_id": new_user.id,
                    "username": new_user.username,
                    "fullname": new_user.fullname,
                    "email": new_user.email,
                    "is_admin": new_user.is_admin,
                    "external_id": external_id
                }
            
            # 缓存用户数据
            memory_cache.set(
                cache_key, 
                result_data,
                expire_seconds=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
            return result_data
            
        except Exception as e:
            em_logger.error(f"验证EGova KB令牌失败: {str(e)}")
            return None
    
    def _generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """
        生成JWT令牌
        
        Args:
            user_data: 用户数据
            
        Returns:
            生成的JWT令牌
        """
        # 设置过期时间
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # 准备payload
        payload = {
            "sub": str(user_data["user_id"]),
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "is_admin": user_data["is_admin"],
            "exp": expire
        }
        
        # 生成令牌
        token = pyjwt.encode(
            payload, 
            settings.JWT_SECRET_KEY, 
            algorithm="HS256"
        )
        
        return token

