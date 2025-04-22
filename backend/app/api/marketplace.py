"""
MCP广场相关API
"""
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from app.services.marketplace.service import marketplace_service


async def list_modules(request: Request):
    """获取所有MCP模块列表"""
    result = marketplace_service.list_modules()
    return JSONResponse(result)


async def get_module(request: Request):
    """获取指定MCP模块详情"""
    module_id = int(request.path_params["module_id"])
    result = marketplace_service.get_module(module_id)
    if result is None:
        return JSONResponse({"detail": "模块不存在"}, status_code=404)
    return JSONResponse(result)


async def get_module_tools(request: Request):
    """获取指定MCP模块的所有工具"""
    module_id = int(request.path_params["module_id"])
    result = marketplace_service.get_module_tools(module_id)
    if result is None:
        return JSONResponse({"detail": "模块不存在"}, status_code=404)
    return JSONResponse(result)


async def get_tool(request: Request):
    """获取指定MCP工具详情"""
    tool_id = int(request.path_params["tool_id"])
    result = marketplace_service.get_tool(tool_id)
    if result is None:
        return JSONResponse({"detail": "工具不存在"}, status_code=404)
    return JSONResponse(result)


async def scan_repository_modules(request: Request):
    """扫描仓库中的MCP模块并更新数据库"""
    result = marketplace_service.scan_repository_modules()
    return JSONResponse(result)


def get_router():
    """获取MCP广场路由"""
    routes = [
        Route("/modules", endpoint=list_modules, methods=["GET"]),
        Route("/modules/{module_id}", endpoint=get_module, methods=["GET"]),
        Route("/modules/{module_id}/tools", endpoint=get_module_tools, 
              methods=["GET"]),
        Route("/tools/{tool_id}", endpoint=get_tool, methods=["GET"]),
        Route("/scan", endpoint=scan_repository_modules, methods=["POST"])
    ]
    
    return routes