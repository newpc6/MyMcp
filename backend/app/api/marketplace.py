"""
MCP广场相关API
"""
from starlette.routing import Route
from starlette.requests import Request
from app.utils.response import success_response, error_response

from app.services.marketplace.service import marketplace_service
from app.utils.logging import mcp_logger
from app.utils.permissions import get_user_info
from app.utils.http.utils import body_page_params


async def page_modules(request: Request):
    """获取MCP模块列表（支持分页）"""
    try:
        data = await request.json()
        condition = data.get("condition", {})
        # 获取分页参数
        page_params = body_page_params(data)
        # 获取用户信息
        user_id, is_admin = get_user_info(request)
        
        # 调用服务层方法
        result = marketplace_service.page_modules(
            page_params=page_params,
            condition=condition,
            user_id=user_id,
            is_admin=is_admin
        )
        return success_response(result)
    except Exception as e:
        mcp_logger.error(f"获取MCP模块列表失败: {str(e)}")
        return error_response(
            f"获取MCP模块列表失败: {str(e)}", 
            code=500, 
            http_status_code=500
        )



async def list_modules(request: Request):
    """获取MCP模块列表（支持分页）"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    # 调用服务层方法，获取包含编辑权限的结果
    result = marketplace_service.list_modules(
        user_id=user_id,
        is_admin=is_admin
    )
    return success_response(result)


async def get_module(request: Request):
    """获取指定MCP模块的详情"""
    module_id = int(request.path_params["module_id"])

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    # 调用服务层方法，获取包含编辑权限的结果
    result = marketplace_service.get_module(
        module_id=module_id,
        user_id=user_id,
        is_admin=is_admin
    )
    if not result:
        return error_response("模块不存在或无权限访问", code=404, http_status_code=404)
    return success_response(result)


async def get_module_tools(request: Request):
    """获取指定MCP模块下的所有工具"""
    module_id = int(request.path_params["module_id"])
    result = marketplace_service.get_module_tools(module_id)
    if result is None:
        return error_response("模块不存在", code=404, http_status_code=404)
    return success_response(result)


async def get_tool(request: Request):
    """获取指定MCP工具的详情"""
    tool_id = int(request.path_params["tool_id"])
    result = marketplace_service.get_tool(tool_id)
    if not result:
        return error_response("工具不存在", code=404, http_status_code=404)
    return success_response(result)


async def scan_repository_modules(request: Request):
    """扫描仓库中的MCP模块并更新数据库"""
    result = marketplace_service.scan_repository_modules()
    return success_response(result)


async def create_module(request: Request):
    """创建新的MCP模块"""
    data = await request.json()

    # 获取用户信息并添加到数据中
    user_id, is_admin = get_user_info(request)
    if user_id:
        data["user_id"] = user_id

    result = marketplace_service.create_module(data)
    return success_response(result, code=0, http_status_code=200)


async def update_module(request: Request):
    """更新MCP模块"""
    module_id = int(request.path_params["module_id"])
    data = await request.json()

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    result = marketplace_service.update_module(
        module_id=module_id,
        data=data,
        user_id=user_id,
        is_admin=is_admin
    )
    if not result:
        return error_response("模块不存在或无权限修改", code=404, http_status_code=404)
    return success_response(result)


async def delete_module(request: Request):
    """删除MCP模块"""
    module_id = int(request.path_params["module_id"])

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    success = marketplace_service.delete_module(
        module_id=module_id,
        user_id=user_id,
        is_admin=is_admin
    )
    if not success:
        return error_response("删除失败或无权限删除", code=400, http_status_code=400)
    return success_response(message="删除成功")


async def publish_module(request: Request):
    """发布模块MCP服务"""
    module_id = int(request.path_params["module_id"])

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    try:
        # 获取配置参数
        data = await request.json()        
        # 提取服务名称，如果配置中包含name字段则使用，否则提示错误
        name = data.get("service_name", None)
        if not name:
            return error_response("服务名称不能为空", code=400, http_status_code=400)

        from app.services.mcp_service.service_manager import service_manager

        # 发布服务
        service = service_manager.publish_service(
            module_id,
            user_id=user_id,
            is_admin=is_admin,
            data=data
        )
        return success_response({
            "message": "服务发布成功",
            "service": service.to_dict()
        })
    except ValueError as e:
        return error_response(str(e), code=400, http_status_code=400)
    except Exception as e:
        mcp_logger.error(f"发布服务失败: {str(e)}")
        return error_response(
            f"发布服务失败: {str(e)}", 
            code=500, 
            http_status_code=500
        )


async def clone_module(request: Request):
    """复制MCP模块"""
    module_id = int(request.path_params["module_id"])
    
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    if not user_id:
        return error_response("需要登录才能复制模块", code=401, http_status_code=401)
    
    # 获取请求体中的自定义数据
    custom_data = {}
    try:
        if request.headers.get("content-type") == "application/json":
            custom_data = await request.json()
    except Exception:
        # 如果解析JSON失败，使用默认值
        pass
    
    # 复制模块
    result = marketplace_service.clone_module(module_id, user_id, custom_data)
    if not result:
        return error_response(
            "复制模块失败，模块可能不存在", 
            code=404, 
            http_status_code=404
        )
    
    return success_response(result, message="模块复制成功")


def get_router():
    """获取MCP广场路由"""
    routes = [
        Route("/modules", list_modules, methods=["GET"]),
        Route("/modules/page", page_modules, methods=["POST"]),
        Route("/modules/{module_id:int}", get_module, methods=["GET"]),
        Route("/modules/{module_id:int}/tools",
              get_module_tools, methods=["GET"]),
        Route("/tools/{tool_id:int}", get_tool, methods=["GET"]),
        Route("/modules/scan", scan_repository_modules, methods=["POST"]),
        Route("/modules", create_module, methods=["POST"]),
        Route("/modules/{module_id:int}", update_module, methods=["PUT"]),
        Route("/modules/{module_id:int}", delete_module, methods=["DELETE"]),

        # 发布模块为服务
        Route("/modules/{module_id:int}/publish",
              publish_module, methods=["POST"]),
        Route("/modules/{module_id:int}/clone",
              clone_module, methods=["POST"]),
    ]
    return routes
