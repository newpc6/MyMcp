"""
Egova AI MCP Server 应用程序入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.urls import get_router  # 导入 urls.py 中的聚合路由
from .middleware.logging_middleware import APILoggingMiddleware
from .utils.logging import em_logger


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        debug=settings.DEBUG
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # 添加日志中间件
    app.add_middleware(APILoggingMiddleware)
    
    # 注册路由
    app = get_router(app)
    
    em_logger.info(f"启动 {settings.API_TITLE} v{settings.API_VERSION}")
    
    return app


app = create_app()


def init_app():
    """
    初始化应用程序
    
    Returns:
        fastapi.FastAPI: FastAPI应用程序实例
    """
    from app.models.engine import init_db
    app = create_app()
    # 初始化数据库
    init_db()
    
    # 返回应用程序实例
    return app 