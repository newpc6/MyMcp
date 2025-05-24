"""
分组相关API
"""
from starlette.requests import Request
from starlette.routing import Route

from app.services.group.service import group_service
from app.utils.response import success_response, error_response
from app.utils.permissions import get_user_info


async def list_group(request: Request):
    """获取所有MCP分组列表"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 调用服务层方法，传递用户信息
    result = group_service.list_group(
        user_id=user_id,
        is_admin=is_admin
    )
    return success_response(result)


async def get_category(request: Request):
    """获取指定MCP分组的详情"""
    category_id = int(request.path_params["category_id"])
    
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 调用服务层方法，传递用户信息
    result = group_service.get_category(
        category_id=category_id,
        user_id=user_id,
        is_admin=is_admin
    )
    if not result:
        return error_response("分组不存在", code=404, http_status_code=404)
    return success_response(result)


async def create_category(request: Request):
    """创建新的MCP分组"""
    data = await request.json()
    
    # 获取用户信息并添加到数据中
    user_id, _ = get_user_info(request)
    if user_id:
        data["user_id"] = user_id
        
    result = group_service.create_category(data)
    return success_response(result, code=0, http_status_code=200)


async def update_category(request: Request):
    """更新MCP分组"""
    category_id = int(request.path_params["category_id"])
    data = await request.json()
    
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 调用服务层方法，传递用户信息
    result = group_service.update_category(
        category_id=category_id,
        data=data,
        user_id=user_id,
        is_admin=is_admin
    )
    if not result:
        return error_response("分组不存在或无权限修改", code=404, http_status_code=404)
    return success_response(result)


async def delete_category(request: Request):
    """删除MCP分组"""
    category_id = int(request.path_params["category_id"])
    
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 调用服务层方法，传递用户信息
    success = group_service.delete_category(
        category_id=category_id,
        user_id=user_id,
        is_admin=is_admin
    )
    if not success:
        return error_response("删除失败或无权限删除", code=400, http_status_code=400)
    return success_response(message="删除成功")


async def update_module_category(request: Request):
    """更新模块所属的分组"""
    module_id = int(request.path_params["module_id"])
    data = await request.json()
    category_id = data.get("category_id")
    
    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    # 调用服务层方法，传递用户信息
    result = group_service.update_module_category(
        module_id=module_id,
        category_id=category_id,
        user_id=user_id,
        is_admin=is_admin
    )
    if not result:
        return error_response("更新失败或无权限修改", code=400, http_status_code=400)
    return success_response(result)


def get_router():
    """获取分组相关路由"""
    routes = [
        Route("/group", list_group, methods=["GET"]),
        Route("/group/{category_id:int}", get_category, methods=["GET"]),
        Route("/group", create_category, methods=["POST"]),
        Route("/group/{category_id:int}", 
              update_category, methods=["PUT"]),
        Route("/group/{category_id:int}", 
              delete_category, methods=["DELETE"]),
        Route("/modules/{module_id:int}/group", 
              update_module_category, methods=["PUT"]),
    ]
    return routes 