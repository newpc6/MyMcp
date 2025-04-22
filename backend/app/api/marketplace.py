"""
MCP广场相关API
"""
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from app.services.marketplace.service import marketplace_service


async def list_modules(request: Request):
    """获取所有MCP模块列表"""
    # 支持按分组查询
    category_id = request.query_params.get("category_id")
    if category_id:
        category_id = int(category_id)
    
    result = marketplace_service.list_modules(category_id=category_id)
    return JSONResponse(result)


async def get_module(request: Request):
    """获取指定MCP模块的详情"""
    module_id = int(request.path_params["module_id"])
    result = marketplace_service.get_module(module_id)
    if not result:
        return JSONResponse({"error": "模块不存在"}, status_code=404)
    return JSONResponse(result)


async def get_module_tools(request: Request):
    """获取指定MCP模块下的所有工具"""
    module_id = int(request.path_params["module_id"])
    result = marketplace_service.get_module_tools(module_id)
    if result is None:
        return JSONResponse({"error": "模块不存在"}, status_code=404)
    return JSONResponse(result)


async def get_tool(request: Request):
    """获取指定MCP工具的详情"""
    tool_id = int(request.path_params["tool_id"])
    result = marketplace_service.get_tool(tool_id)
    if not result:
        return JSONResponse({"error": "工具不存在"}, status_code=404)
    return JSONResponse(result)


async def scan_repository_modules(request: Request):
    """扫描仓库中的MCP模块并更新数据库"""
    result = marketplace_service.scan_repository_modules()
    return JSONResponse(result)


async def create_module(request: Request):
    """创建新的MCP模块"""
    data = await request.json()
    result = marketplace_service.create_module(data)
    return JSONResponse(result, status_code=201)


async def update_module(request: Request):
    """更新MCP模块"""
    module_id = int(request.path_params["module_id"])
    data = await request.json()
    result = marketplace_service.update_module(module_id, data)
    if not result:
        return JSONResponse({"error": "模块不存在"}, status_code=404)
    return JSONResponse(result)


async def delete_module(request: Request):
    """删除MCP模块"""
    module_id = int(request.path_params["module_id"])
    success = marketplace_service.delete_module(module_id)
    if not success:
        return JSONResponse({"error": "删除失败"}, status_code=400)
    return JSONResponse({"message": "删除成功"})


async def list_categories(request: Request):
    """获取所有MCP分组列表"""
    result = marketplace_service.list_categories()
    return JSONResponse(result)


async def get_category(request: Request):
    """获取指定MCP分组的详情"""
    category_id = int(request.path_params["category_id"])
    result = marketplace_service.get_category(category_id)
    if not result:
        return JSONResponse({"error": "分组不存在"}, status_code=404)
    return JSONResponse(result)


async def create_category(request: Request):
    """创建新的MCP分组"""
    data = await request.json()
    result = marketplace_service.create_category(data)
    return JSONResponse(result, status_code=201)


async def update_category(request: Request):
    """更新MCP分组"""
    category_id = int(request.path_params["category_id"])
    data = await request.json()
    result = marketplace_service.update_category(category_id, data)
    if not result:
        return JSONResponse({"error": "分组不存在"}, status_code=404)
    return JSONResponse(result)


async def delete_category(request: Request):
    """删除MCP分组"""
    category_id = int(request.path_params["category_id"])
    success = marketplace_service.delete_category(category_id)
    if not success:
        return JSONResponse({"error": "删除失败"}, status_code=400)
    return JSONResponse({"message": "删除成功"})


async def update_module_category(request: Request):
    """更新模块所属的分组"""
    module_id = int(request.path_params["module_id"])
    data = await request.json()
    category_id = data.get("category_id")
    
    result = marketplace_service.update_module_category(module_id, category_id)
    if not result:
        return JSONResponse({"error": "更新失败"}, status_code=400)
    return JSONResponse(result)


def get_router():
    """获取MCP广场路由"""
    routes = [
        Route("/modules", list_modules, methods=["GET"]),
        Route("/modules/{module_id:int}", get_module, methods=["GET"]),
        Route("/modules/{module_id:int}/tools", get_module_tools, methods=["GET"]),
        Route("/tools/{tool_id:int}", get_tool, methods=["GET"]),
        Route("/modules/scan", scan_repository_modules, methods=["POST"]),
        Route("/modules", create_module, methods=["POST"]),
        Route("/modules/{module_id:int}", update_module, methods=["PUT"]),
        Route("/modules/{module_id:int}", delete_module, methods=["DELETE"]),
        Route("/categories", list_categories, methods=["GET"]),
        Route("/categories/{category_id:int}", get_category, methods=["GET"]),
        Route("/categories", create_category, methods=["POST"]),
        Route("/categories/{category_id:int}", update_category, methods=["PUT"]),
        Route("/categories/{category_id:int}", delete_category, methods=["DELETE"]),
        Route(
            "/modules/{module_id:int}/category", 
            update_module_category, 
            methods=["PUT"]
        ),
    ]
    return routes
