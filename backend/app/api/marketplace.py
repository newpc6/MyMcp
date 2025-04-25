"""
MCP广场相关API
"""
from starlette.routing import Route
from starlette.requests import Request
from app.utils.response import success_response, error_response

from app.services.marketplace.service import marketplace_service
from app.services.mcp_service.service_manager import service_manager
from app.utils.logging import em_logger


async def list_modules(request: Request):
    """获取所有MCP模块列表"""
    # 支持按分组查询
    category_id = request.query_params.get("category_id")
    if category_id:
        category_id = int(category_id)

    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False

    result = marketplace_service.list_modules(
        category_id=category_id,
        user_id=user_id,
        is_admin=is_admin
    )
    return success_response(result)


async def get_module(request: Request):
    """获取指定MCP模块的详情"""
    module_id = int(request.path_params["module_id"])

    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False

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
    user = request.state.user
    if user:
        data["user_id"] = user.get("user_id")

    result = marketplace_service.create_module(data)
    return success_response(result, code=0, http_status_code=201)


async def update_module(request: Request):
    """更新MCP模块"""
    module_id = int(request.path_params["module_id"])
    data = await request.json()

    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False

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
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False

    success = marketplace_service.delete_module(
        module_id=module_id,
        user_id=user_id,
        is_admin=is_admin
    )
    if not success:
        return error_response("删除失败或无权限删除", code=400, http_status_code=400)
    return success_response(message="删除成功")


async def list_categories(request: Request):
    """获取所有MCP分组列表"""
    result = marketplace_service.list_categories()
    return success_response(result)


async def get_category(request: Request):
    """获取指定MCP分组的详情"""
    category_id = int(request.path_params["category_id"])
    result = marketplace_service.get_category(category_id)
    if not result:
        return error_response("分组不存在", code=404, http_status_code=404)
    return success_response(result)


async def create_category(request: Request):
    """创建新的MCP分组"""
    data = await request.json()
    result = marketplace_service.create_category(data)
    return success_response(result, code=0, http_status_code=201)


async def update_category(request: Request):
    """更新MCP分组"""
    category_id = int(request.path_params["category_id"])
    data = await request.json()
    result = marketplace_service.update_category(category_id, data)
    if not result:
        return error_response("分组不存在", code=404, http_status_code=404)
    return success_response(result)


async def delete_category(request: Request):
    """删除MCP分组"""
    category_id = int(request.path_params["category_id"])
    success = marketplace_service.delete_category(category_id)
    if not success:
        return error_response("删除失败", code=400, http_status_code=400)
    return success_response(message="删除成功")


async def update_module_category(request: Request):
    """更新模块所属的分组"""
    module_id = int(request.path_params["module_id"])
    data = await request.json()
    category_id = data.get("category_id")

    result = marketplace_service.update_module_category(module_id, category_id)
    if not result:
        return error_response("更新失败", code=400, http_status_code=400)
    return success_response(result)


async def publish_module(request: Request):
    """发布模块MCP服务"""
    module_id = int(request.path_params["module_id"])
    
    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False
    
    try:
        # 获取配置参数
        config_params = await request.json()
        
        from app.services.mcp_service.service_manager import service_manager
        
        # 发布服务
        service = service_manager.publish_service(
            module_id, 
            user_id=user_id, 
            is_admin=is_admin,
            config_params=config_params
        )
        return success_response({
            "message": "服务发布成功",
            "service": service.to_dict()
        })
    except ValueError as e:
        return error_response(str(e), code=400, http_status_code=400)
    except Exception as e:
        em_logger.error(f"发布服务失败: {str(e)}")
        return error_response(f"发布服务失败: {str(e)}", code=500, http_status_code=500)


async def stop_service(request: Request):
    """停止服务"""
    service_uuid = request.path_params["service_uuid"]
    
    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False
    
    try:
        from app.services.mcp_service.service_manager import service_manager
        
        # 停止服务
        result = service_manager.stop_service(
            service_uuid,
            user_id=user_id,
            is_admin=is_admin
        )
        if not result:
            return error_response("停止服务失败，服务可能不存在", code=400, http_status_code=400)
            
        return success_response({"message": "服务已停止"})
    except ValueError as e:
        # 权限错误
        return error_response(str(e), code=403, http_status_code=403)
    except Exception as e:
        em_logger.error(f"停止服务失败: {str(e)}")
        return error_response(f"停止服务失败: {str(e)}", code=500, http_status_code=500)


async def start_service(request: Request):
    """启动服务"""
    service_uuid = request.path_params["service_uuid"]
    
    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False
    
    try:
        from app.services.mcp_service.service_manager import service_manager
        
        # 启动服务
        result = service_manager.start_service(
            service_uuid,
            user_id=user_id,
            is_admin=is_admin
        )
        if not result:
            return error_response("启动服务失败，服务可能不存在", code=400, http_status_code=400)
            
        return success_response({"message": "服务已启动"})
    except Exception as e:
        em_logger.error(f"启动服务失败: {str(e)}")
        return error_response(f"启动服务失败: {str(e)}", code=500, http_status_code=500)


async def uninstall_service(request: Request):
    """卸载服务"""
    service_uuid = request.path_params["service_uuid"]
    
    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False
    
    try:
        from app.services.mcp_service.service_manager import service_manager
        
        # 删除服务
        result = service_manager.delete_service(
            service_uuid,
            user_id=user_id,
            is_admin=is_admin
        )
        if not result:
            return error_response("卸载服务失败，服务可能不存在", code=400, http_status_code=400)
            
        return success_response({"message": "服务已卸载"})
    except Exception as e:
        em_logger.error(f"卸载服务失败: {str(e)}")
        return error_response(f"卸载服务失败: {str(e)}", code=500, http_status_code=500)


async def update_service_description(request: Request):
    """更新服务描述"""
    service_uuid = request.path_params["service_uuid"]
    data = await request.json()
    description = data.get("description", "")

    try:
        from app.models.engine import get_db
        from app.models.modules.mcp_services import McpService

        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()

            if not service:
                return error_response("服务不存在", code=404, http_status_code=404)

            # 获取关联的模块并更新描述
            from app.models.modules.mcp_marketplace import McpModule
            module = db.query(McpModule).filter(
                McpModule.id == service.module_id
            ).first()

            if module:
                module.description = description
                db.commit()
                return success_response(message="服务说明已更新")
            else:
                return error_response("未找到关联模块", code=404, http_status_code=404)
    except Exception as e:
        return error_response(f"更新服务说明失败: {str(e)}", code=500, http_status_code=500)


async def list_services(request: Request):
    """列出所有服务"""
    # 获取模块ID参数
    module_id = request.query_params.get("module_id")
    if module_id:
        module_id = int(module_id)
        
    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False
    
    try:
        from app.services.mcp_service.service_manager import service_manager
        
        # 获取服务列表
        services = service_manager.list_services(
            module_id=module_id,
            user_id=user_id,
            is_admin=is_admin
        )
        return success_response(services)
    except Exception as e:
        em_logger.error(f"获取服务列表失败: {str(e)}")
        return error_response(f"获取服务列表失败: {str(e)}", code=500, http_status_code=500)


async def get_service(request: Request):
    """获取服务详情"""
    service_uuid = request.path_params["service_uuid"]
    
    # 获取用户信息
    user = request.state.user
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False
    
    try:
        from app.services.mcp_service.service_manager import service_manager
        
        # 获取服务状态
        service = service_manager.get_service_status(service_uuid)
        if not service:
            return error_response("服务不存在", code=404, http_status_code=404)
            
        # 非管理员只能查看自己的服务
        if not is_admin and user_id is not None and service.get("user_id") != user_id:
            return error_response("无权访问此服务", code=403, http_status_code=403)
            
        return success_response(service)
    except Exception as e:
        em_logger.error(f"获取服务状态失败: {str(e)}")
        return error_response(f"获取服务状态失败: {str(e)}", code=500, http_status_code=500)


async def get_online_services(request: Request):
    """获取在线服务列表"""
    # 获取运行中的服务UUID列表
    online_services = list(service_manager._running_services.keys())
    return success_response(online_services)


def get_router():
    """获取MCP广场路由"""
    routes = [
        Route("/modules", list_modules, methods=["GET"]),
        Route("/modules/{module_id:int}", get_module, methods=["GET"]),
        Route("/modules/{module_id:int}/tools",
              get_module_tools, methods=["GET"]),
        Route("/tools/{tool_id:int}", get_tool, methods=["GET"]),
        Route("/modules/scan", scan_repository_modules, methods=["POST"]),
        Route("/modules", create_module, methods=["POST"]),
        Route("/modules/{module_id:int}", update_module, methods=["PUT"]),
        Route("/modules/{module_id:int}", delete_module, methods=["DELETE"]),
        Route("/categories", list_categories, methods=["GET"]),
        Route("/categories/{category_id:int}", get_category, methods=["GET"]),
        Route("/categories", create_category, methods=["POST"]),
        Route("/categories/{category_id:int}",
              update_category, methods=["PUT"]),
        Route("/categories/{category_id:int}",
              delete_category, methods=["DELETE"]),
        Route(
            "/modules/{module_id:int}/category",
            update_module_category,
            methods=["PUT"]
        ),

        # 服务相关路由
        Route("/modules/{module_id:int}/publish",
              publish_module, methods=["POST"]),
        Route("/services", list_services, methods=["GET"]),
        Route("/services/online", get_online_services, methods=["GET"]),
        Route("/services/{service_uuid}", get_service, methods=["GET"]),
        Route("/services/{service_uuid}/stop", stop_service, methods=["POST"]),
        Route("/services/{service_uuid}/start",
              start_service, methods=["POST"]),
        Route("/services/{service_uuid}/uninstall",
              uninstall_service, methods=["POST"]),
        Route("/services/{service_uuid}/description",
              update_service_description, methods=["PUT"]),
    ]
    return routes
