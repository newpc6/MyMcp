"""
日志中间件

用于记录API请求和响应
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ..utils.logging import log_api_call


class APILoggingMiddleware(BaseHTTPMiddleware):
    """API日志中间件，记录所有API请求和响应"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并记录日志
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            响应对象
        """
        # 记录请求日志
        log_api_call(request)
        
        try:
            # 处理请求
            response = await call_next(request)
            # 记录响应日志
            log_api_call(request, response)
            return response
        except Exception as e:
            # 记录异常日志
            log_api_call(request, error=e)
            raise 