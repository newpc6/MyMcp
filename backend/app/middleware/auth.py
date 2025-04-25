"""
认证中间件模块

使用Starlette实现的身份验证中间件
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import Response
from app.services.users import UserService
from app.utils.response import error_response
from app.utils.logging import em_logger
from app.core.config import settings
# 重命名以确保使用正确的PyJWT库
import jwt as pyjwt
import os
from typing import Optional, Tuple, Dict, Any


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件，验证用户登录状态和权限"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.public_paths = [
            "/api/auth/login", 
            "/api/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        self.sse_paths = [
            "/sse",
            "/messages/"
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        处理请求并验证认证信息
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            响应对象
        """
        # 检查是否是公开路径
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # 验证token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return error_response(
                message="未登录", 
                code=401, 
                http_status_code=401
            )
        
        token = auth_header.replace("Bearer ", "")
        try:
            # 验证并解析token
            user_data, is_valid = self._validate_token(token)
            if not is_valid or not user_data:
                return error_response(
                    message="未登录或会话已过期", 
                    code=401, 
                    http_status_code=401
                )
            
            # 将用户信息添加到请求状态
            request.state.user = user_data
            
            # 检查是否需要管理员权限
            if (self._requires_admin(request.url.path) and 
                    not user_data.get("is_admin", False)):
                return error_response(
                    message="需要管理员权限", 
                    code=403, 
                    http_status_code=403
                )
            
            # 继续处理请求
            return await call_next(request)
        except Exception as e:
            return error_response(
                message=f"认证失败: {str(e)}", 
                code=401, 
                http_status_code=401
            )
    
    def _is_public_path(self, path: str) -> bool:
        """检查路径是否为公开路径"""
        public = any(
            path.startswith(public_path) 
            for public_path in self.public_paths
        )
        sse = any(
            path.endswith(sse_path)
            for sse_path in self.sse_paths
        )
        return public or sse
    
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
            # 从环境变量或配置中获取密钥
            # secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key")
            secret_key = settings.JWT_SECRET_KEY
            payload = pyjwt.decode(token, secret_key, algorithms=["HS256"])
            
            # 支持从user_id或sub字段获取用户ID
            user_id = payload.get("user_id") or payload.get("sub")
            if not user_id:
                em_logger.warning("JWT中没有找到user_id或sub字段")
                return None, False
            
            # 验证用户是否存在
            user = UserService.get_user_by_id(user_id)
            if not user:
                em_logger.warning(f"未找到ID为{user_id}的用户")
                return None, False
            
            # 返回用户数据
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "is_admin": user.is_admin
            }
            
            return user_data, True
        except pyjwt.PyJWTError as e:
            em_logger.error(f"JWT解码失败: {str(e)}")
            return None, False
        except Exception as e:
            em_logger.error(f"JWT解码失败: {str(e)}")
            return None, False 