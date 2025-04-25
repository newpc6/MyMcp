"""
API路由模块

提供所有API的路由配置
"""
from app.core.config import settings
from app.utils.response import success_response
from . import (
    auth, tools, mcp_service, history,
    execution, log, marketplace
)


async def root(request):
    """API根路由"""
    return success_response({
        "title": settings.API_TITLE,
        "version": settings.API_VERSION
    }, message=f"欢迎使用 {settings.API_TITLE} v{settings.API_VERSION}")


def get_router(app):
    """获取所有API路由"""
    # 添加根路由
    app.add_route("/", root)
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
        app.add_route(
            f"{settings.API_PREFIX}/mcp/service{route.path}", 
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
    
    return app
