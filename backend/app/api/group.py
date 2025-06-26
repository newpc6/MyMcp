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


async def stat_group(request: Request):
    """获取MCP分组统计信息排行榜
    
    查询参数:
        order_by (str): 排序字段，可选值: templates_count, services_count, call_count
        limit (int): 返回数量限制，1-100之间，默认10
        desc (bool): 是否降序排列，默认true
    
    示例:
        POST /group/stat
        Content-Type: application/json
        {
            "order_by": "services_count",
            "limit": 5,
            "desc": true
        }
    
    返回:
        成功: {"code": 0, "data": [...], "message": "success"}
        失败: {"code": 400/500, "data": null, "message": "错误信息"}
    """
    try:
        # 获取用户信息
        user_id, is_admin = get_user_info(request)
        
        # 获取查询参数
        data = await request.json()
        
        # 解析参数
        order_by = data.get("order_by", "templates_count")
        limit = int(data.get("limit", 10))
        desc = data.get("desc", True)
        
        # 参数验证
        valid_order_fields = ["templates_count", "services_count", "call_count"]
        if order_by not in valid_order_fields:
            fields_str = ', '.join(valid_order_fields)
            msg = f"无效的排序字段: {order_by}，支持的字段: {fields_str}"
            return error_response(msg, code=400, http_status_code=400)
        
        # 限制数量范围
        if limit < 1 or limit > 100:
            return error_response(
                "limit参数必须在1-100之间",
                code=400,
                http_status_code=400
            )
        
        # 调用服务层方法
        result = group_service.stat_group(
            order_by=order_by,
            limit=limit,
            desc=desc,
            user_id=user_id,
            is_admin=is_admin
        )
        
        return success_response(result)
        
    except ValueError as e:
        return error_response(
            f"参数错误: {str(e)}",
            code=400,
            http_status_code=400
        )
    except Exception as e:
        from app.utils.logging import mcp_logger
        mcp_logger.error(f"获取分组统计信息失败: {str(e)}")
        return error_response(
            f"获取分组统计信息失败: {str(e)}",
            code=500,
            http_status_code=500
        )


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
        Route("/group/stat", stat_group, methods=["POST"]),
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