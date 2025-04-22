from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from ..models.modules.schemas import ModuleCreate, ModuleUpdate
from ..services.modules.service import ModuleService

module_service = ModuleService()


async def get_modules(request: Request):
    """获取所有模块信息"""
    result = module_service.get_all_modules()
    return JSONResponse(result)


async def list_modules(request: Request):
    """获取所有模块路径列表"""
    result = module_service.list_modules()
    return JSONResponse(result)


async def get_module_count(request: Request):
    """获取模块数量"""
    result = {"count": module_service.get_module_count()}
    return JSONResponse(result)


async def get_module(request: Request):
    """获取模块内容"""
    module_path = request.path_params["module_path"]
    try:
        result = module_service.get_module_content(module_path)
        return JSONResponse(result)
    except FileNotFoundError:
        return JSONResponse({"detail": "Module not found"}, status_code=404)


async def update_module(request: Request):
    """更新模块内容"""
    module_path = request.path_params["module_path"]
    try:
        data = await request.json()
        module_update = ModuleUpdate(**data)
        
        module_service.update_module(
            module_path, 
            module_update.content
        )
        return JSONResponse({"message": "Module updated successfully"})
    except FileNotFoundError:
        return JSONResponse({"detail": "Module not found"}, status_code=404)


async def create_module(request: Request):
    """创建新模块"""
    try:
        data = await request.json()
        module_create = ModuleCreate(**data)
        
        module_service.create_module(
            module_create.path, 
            module_create.content
        )
        return JSONResponse({"message": "Module created successfully"})
    except FileExistsError:
        return JSONResponse({"detail": "Module already exists"}, status_code=409)


async def delete_module(request: Request):
    """删除模块"""
    module_path = request.path_params["module_path"]
    try:
        module_service.delete_module(module_path)
        return JSONResponse({"message": "Module deleted successfully"})
    except FileNotFoundError:
        return JSONResponse({"detail": "Module not found"}, status_code=404)


def get_router():
    """获取模块路由"""
    routes = [
        Route("/", endpoint=get_modules, methods=["GET"]),
        Route("/list", endpoint=list_modules, methods=["GET"]),
        Route("/count", endpoint=get_module_count, methods=["GET"]),
        Route(
            "/{module_path:path}", 
            endpoint=get_module, 
            methods=["GET"]
        ),
        Route(
            "/{module_path:path}", 
            endpoint=update_module, 
            methods=["PUT"]
        ),
        Route("/", endpoint=create_module, methods=["POST"]),
        Route(
            "/{module_path:path}", 
            endpoint=delete_module, 
            methods=["DELETE"]
        )
    ]
    
    return routes 