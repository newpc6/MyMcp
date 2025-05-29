"""
API路由模块

提供所有API的路由配置
"""
from app.core.config import settings
from app.utils.response import success_response
from starlette.routing import Mount
from starlette.responses import FileResponse
import os
from . import (
    auth, tools, mcp_service, history,
    execution, log, marketplace, statistics, static, group
)
from app.utils.logging import mcp_logger

async def api_root(request):
    """API根路由"""
    return success_response({
        "title": settings.API_TITLE,
        "version": settings.API_VERSION
    }, message=f"欢迎使用 {settings.API_TITLE} v{settings.API_VERSION}")


def get_router(app) -> None:
    """
    注册所有API路由
    
    Args:
        app: 应用实例
    """
    # 添加API根路由
    app.add_route(f"{settings.API_PREFIX}", api_root)
    
    # 添加认证中间件
    from app.middleware.auth import AuthMiddleware
    app.add_middleware(AuthMiddleware)
    
    # 添加认证路由
    for route in auth.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/auth{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加工具路由
    for route in tools.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/tools{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加MCP服务路由
    for route in mcp_service.get_router():
        mcp_logger.info(f"添加MCP服务路由: {settings.API_PREFIX}/service{route.path}")
        app.add_route(
            f"{settings.API_PREFIX}/service{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加历史记录路由
    for route in history.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/history{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加执行路由
    for route in execution.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/execute{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加日志路由
    for route in log.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/log{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加MCP广场路由
    for route in marketplace.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/marketplace{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加分组路由
    for route in group.get_router():
        app.add_route(
            f"{settings.API_PREFIX}{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
        
    for route in statistics.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/statistics{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加静态资源路由 - 移到最后注册，确保API路由优先匹配
    try:
        # 添加静态文件路由
        for route in static.get_router():
            app.add_route(
                route["path"],
                route["endpoint"],
                methods=route["methods"],
                name=route["name"]
            )
            mcp_logger.info(f"添加静态文件路由: {route['path']}")
    except Exception as e:
        mcp_logger.error(f"配置静态资源路由时出错: {str(e)}")

    return app
