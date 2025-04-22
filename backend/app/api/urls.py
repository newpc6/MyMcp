from starlette.responses import JSONResponse
from app.core.config import settings
from . import (
    tools, resources, modules, protocols, mcp_service, 
    history, execution, log
)


async def root(request):
    """API根路径处理函数"""
    return JSONResponse({"message": "欢迎使用 Egova AI MCP Server API"})


def get_router(app):
    """获取所有API路由"""
    # 添加根路由
    app.add_route("/", root)
    
    # 添加工具路由
    for route in tools.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/tools{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加资源路由
    for route in resources.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/resources{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加模块路由
    for route in modules.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/modules{route.path}", 
            route.endpoint, 
            methods=route.methods, 
            name=route.name
        )
    
    # 添加协议路由
    for route in protocols.get_router():
        app.add_route(
            f"{settings.API_PREFIX}/protocols{route.path}", 
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
    
    return app
