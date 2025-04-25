"""
中间件初始化

用于初始化和注册中间件
"""

from .logging_middleware import APILoggingMiddleware

__all__ = ["APILoggingMiddleware"]

# 未使用auth中间件，而是在urls.py中通过装饰器使用auth.auth_middleware 