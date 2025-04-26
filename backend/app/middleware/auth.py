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
import time
from typing import Optional, Tuple, Dict, Any


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件，验证用户登录状态和权限"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # API相关公开路径
        self.public_api_paths = [
            "/api/auth/login", 
            "/api/auth/register",
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
            return error_response(status_code=401, message="未提供认证令牌")
            
        # 提取令牌
        token = auth_header.replace("Bearer ", "")
        if not token:
            return error_response(status_code=401, message="无效的认证令牌格式")
            
        # 验证令牌
        user_data, is_valid = self._validate_token(token)
        if not is_valid:
            return error_response(status_code=401, message="认证令牌无效或已过期")
            
        # 检查权限
        if self._requires_admin(request.url.path) and not user_data.get("is_admin", False):
            return error_response(status_code=403, message="需要管理员权限")
            
        # 将用户数据添加到请求中
        request.state.user = user_data
        
        # 继续处理请求
        return await call_next(request)
    
    def _is_public_api_path(self, path: str) -> bool:
        """检查路径是否为公开API路径"""
        return any(
            path.startswith(public_path) 
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
            
            # 返回用户数据
            return payload, True
        except Exception as e:
            em_logger.error(f"令牌验证失败: {str(e)}")
            return None, False 