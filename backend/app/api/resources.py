from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from ..models.resources.schemas import ResourceCreate, ResourceUpdate
from ..services.resources.service import ResourceService

resource_service = ResourceService()


async def get_resources(request: Request):
    """获取所有资源信息"""
    result = resource_service.get_all_resources()
    return JSONResponse(result)


async def list_resources(request: Request):
    """获取所有资源路径列表"""
    result = resource_service.list_resources()
    return JSONResponse(result)


async def get_resource_info(request: Request):
    """获取特定资源信息"""
    resource_path = request.path_params["resource_path"]
    try:
        result = resource_service.get_resource_info(resource_path)
        return JSONResponse(result)
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=404)


async def get_resource(request: Request):
    """获取资源内容"""
    resource_path = request.path_params["resource_path"]
    try:
        result = resource_service.get_resource_content(resource_path)
        return JSONResponse(result)
    except FileNotFoundError:
        return JSONResponse({"detail": "Resource not found"}, status_code=404)


async def update_resource(request: Request):
    """更新资源内容"""
    resource_path = request.path_params["resource_path"]
    try:
        data = await request.json()
        resource_update = ResourceUpdate(**data)
        
        resource_service.update_resource(
            resource_path, 
            resource_update.content
        )
        return JSONResponse({"message": "Resource updated successfully"})
    except FileNotFoundError:
        return JSONResponse({"detail": "Resource not found"}, status_code=404)


async def create_resource(request: Request):
    """创建新资源"""
    try:
        data = await request.json()
        resource_create = ResourceCreate(**data)
        
        resource_service.create_resource(
            resource_create.path, 
            resource_create.content
        )
        return JSONResponse({"message": "Resource created successfully"})
    except FileExistsError:
        return JSONResponse(
            {"detail": "Resource already exists"}, status_code=409
        )


async def delete_resource(request: Request):
    """删除资源"""
    resource_path = request.path_params["resource_path"]
    try:
        resource_service.delete_resource(resource_path)
        return JSONResponse({"message": "Resource deleted successfully"})
    except FileNotFoundError:
        return JSONResponse({"detail": "Resource not found"}, status_code=404)


def get_router():
    """获取资源路由"""
    routes = [
        Route("/", endpoint=get_resources, methods=["GET"]),
        Route("/list", endpoint=list_resources, methods=["GET"]),
        Route("/info/{resource_path:path}", endpoint=get_resource_info, 
              methods=["GET"]),
        Route("/{resource_path:path}", endpoint=get_resource, 
              methods=["GET"]),
        Route("/{resource_path:path}", endpoint=update_resource, 
              methods=["PUT"]),
        Route("/", endpoint=create_resource, methods=["POST"]),
        Route("/{resource_path:path}", endpoint=delete_resource, 
              methods=["DELETE"])
    ]
    
    return routes 