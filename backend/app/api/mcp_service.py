from starlette.routing import Route
from starlette.requests import Request
from pydantic import BaseModel, ValidationError
import importlib

from app.utils.response import success_response, error_response
from app.server.mcp_server import (
    add_tool, remove_tool, restart_mcp_server, check_mcp_status, get_enabled_tools, update_service_params
)
from app.utils.permissions import add_edit_permission, get_user_info
from app.utils.logging import mcp_logger
from app.utils.http.utils import body_page_params
from app.services.mcp_service.service_manager import service_manager


class ToolLoadRequest(BaseModel):
    """加载工具请求模型"""
    module_path: str  # 模块路径，例如 "repository.demo_tool"
    function_name: str  # 函数名称
    tool_name: str = None  # 可选的工具名称，默认使用函数名
    description: str = None  # 可选的工具描述


class ToolRemoveRequest(BaseModel):
    """移除工具请求模型"""
    tool_name: str  # 工具名称


async def load_tool(request: Request):
    """动态加载工具"""
    try:
        # 解析请求数据
        data = await request.json()
        request_data = ToolLoadRequest(**data)

        # 动态导入模块
        try:
            module = importlib.import_module(request_data.module_path)
        except ImportError as e:
            error_msg = f"模块 {request_data.module_path} 导入失败: {str(e)}"
            return error_response(error_msg, code=404, http_status_code=404)

        # 获取函数
        if not hasattr(module, request_data.function_name):
            error_msg = (f"函数 {request_data.function_name} 在模块 "
                         f"{request_data.module_path} 中不存在")
            return error_response(error_msg, code=404, http_status_code=404)

        func = getattr(module, request_data.function_name)

        # 添加为工具
        add_tool(
            func=func,
            name=request_data.tool_name,
            doc=request_data.description
        )

        tool_name = request_data.tool_name or request_data.function_name
        return success_response({
            "tool_name": tool_name
        }, message=f"工具 {tool_name} 已成功加载")
    except ValidationError as e:
        return error_response(str(e), code=422, http_status_code=422)
    except Exception as e:
        return error_response(
            f"加载工具失败: {str(e)}", code=500, http_status_code=500
        )


async def unload_tool(request: Request):
    """动态卸载工具"""
    try:
        data = await request.json()
        request_data = ToolRemoveRequest(**data)

        success = remove_tool(request_data.tool_name)
        if success:
            return success_response(
                message=f"工具 {request_data.tool_name} 已成功卸载"
            )
        else:
            error_msg = f"工具 {request_data.tool_name} 不存在或卸载失败"
            return error_response(error_msg, code=404, http_status_code=404)
    except ValidationError as e:
        return error_response(str(e), code=422, http_status_code=422)
    except Exception as e:
        return error_response(
            f"卸载工具失败: {str(e)}", code=500, http_status_code=500
        )


async def restart_service(request: Request):
    """重启MCP服务"""
    try:
        success = restart_mcp_server()
        if success:
            return success_response(message="MCP服务已成功重启")
        else:
            msg = "MCP服务重启失败"
            return error_response(msg, code=500, http_status_code=500)
    except Exception as e:
        return error_response(
            f"重启服务失败: {str(e)}", code=500, http_status_code=500
        )


async def get_status(request: Request):
    """获取MCP服务状态"""
    try:
        # 获取用户信息
        user_id, is_admin = get_user_info(request)

        # 获取服务状态
        status = check_mcp_status()

        # 添加可编辑字段
        status = add_edit_permission(status, user_id, is_admin)

        return success_response(status)
    except Exception as e:
        error_msg = f"获取服务状态失败: {str(e)}"
        return error_response(error_msg, code=500, http_status_code=500)


async def enabled_tools(request: Request):
    """获取当前启用的工具列表"""
    try:
        # 获取用户信息
        user_id, is_admin = get_user_info(request)

        # 获取工具列表
        tools_list = get_enabled_tools()

        # 添加可编辑字段
        tools_list = add_edit_permission(tools_list, user_id, is_admin)

        return success_response({
            "enabled_tools": tools_list,
            "count": len(tools_list)
        })
    except Exception as e:
        error_msg = f"获取启用工具列表失败: {str(e)}"
        return error_response(error_msg, code=500, http_status_code=500)


async def update_params(request: Request):
    """更新服务参数"""
    try:
        data = await request.json()
        id = request.path_params["id"]
        if data.get("config_params"):
            if isinstance(data.get("config_params"), str):
                data = data.get("config_params")
        # 更新服务参数
        update_service_params(id, data)
        return success_response(message="服务参数更新成功")
    except Exception as e:
        mcp_logger.error(f"更新服务参数失败: {str(e)}")
        return error_response(
            f"更新服务参数失败: {str(e)}", code=500, http_status_code=500
        )


# 以下是从marketplace.py迁移过来的service相关接口


async def list_services(request: Request):
    """列出所有服务"""
    # 获取模块ID参数
    module_id = request.query_params.get("module_id")
    if module_id:
        module_id = int(module_id)

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    try:
        # 获取服务列表（包含编辑权限信息）
        services = service_manager.list_services(
            module_id=module_id,
            user_id=user_id,
            is_admin=is_admin,
            request=request  # 传递请求对象
        )
        return success_response(services)
    except Exception as e:
        mcp_logger.error(f"获取服务列表失败: {str(e)}")
        err_msg = f"获取服务列表失败: {str(e)}"
        return error_response(err_msg, code=500, http_status_code=500)


async def create_third_party_service(request: Request):
    """创建第三方MCP服务"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    try:
        # 获取服务数据
        data = await request.json()
        # 验证必填字段
        name = data.get("service_name", None)
        sse_url = data.get("sse_url", None)

        if not name:
            return error_response("服务名称不能为空", code=400, http_status_code=400)
        if not sse_url:
            return error_response("SSE URL不能为空", code=400, http_status_code=400)

        from app.services.mcp_service.service_manager import service_manager

        # 创建第三方服务
        service = service_manager.publish_third_party_service(
            user_id=user_id,
            is_admin=is_admin,
            data=data
        )
        return success_response({
            "message": "第三方服务创建成功",
            "service": service.to_dict()
        })
    except ValueError as e:
        return error_response(str(e), code=400, http_status_code=400)
    except Exception as e:
        mcp_logger.error(f"创建第三方服务失败: {str(e)}")
        return error_response(
            f"创建第三方服务失败: {str(e)}",
            code=500,
            http_status_code=500
        )


async def page_services(request: Request):
    """分页查询服务列表"""
    try:
        # 获取请求体数据
        data = await request.json()

        # 获取用户信息
        user_id, is_admin = get_user_info(request)
        # 从请求体中解析分页参数和搜索条件
        page_params = body_page_params(data)

        # 获取搜索条件
        condition = data.get("condition", {})
        # 获取分页服务列表
        result = service_manager.page_services(
            page_params=page_params,
            user_id=user_id,
            is_admin=is_admin,
            condition=condition,
            request=request
        )

        return success_response(result)
    except Exception as e:
        mcp_logger.error(f"分页查询服务列表失败: {str(e)}")
        err_msg = f"分页查询服务列表失败: {str(e)}"
        return error_response(err_msg, code=500, http_status_code=500)


async def get_service(request: Request):
    """获取服务详情"""
    service_uuid = request.path_params["service_uuid"]

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    try:
        # 获取服务状态（包含编辑权限信息）
        service = service_manager.get_service_status(
            service_uuid,
            request=request,  # 传递请求对象
            user_id=user_id,
            is_admin=is_admin
        )
        if not service:
            return error_response("服务不存在", code=404, http_status_code=404)

        # 非管理员只能查看自己的服务
        if (not is_admin and user_id is not None and
                service.get("user_id") != user_id):
            msg = "无权访问此服务"
            return error_response(msg, code=403, http_status_code=403)

        return success_response(service)
    except Exception as e:
        mcp_logger.error(f"获取服务状态失败: {str(e)}")
        err_msg = f"获取服务状态失败: {str(e)}"
        return error_response(err_msg, code=500, http_status_code=500)


async def get_online_services(request: Request):
    """获取在线服务列表"""
    try:
        # 获取运行中的服务UUID列表
        online_services = list(service_manager._running_services.keys())
        return success_response(online_services)
    except Exception as e:
        mcp_logger.error(f"获取在线服务失败: {str(e)}")
        return error_response(
            f"获取在线服务失败: {str(e)}", code=500, http_status_code=500
        )


async def stop_service(request: Request):
    """停止服务"""
    service_uuid = request.path_params["service_uuid"]

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    try:
        # 停止服务
        result = service_manager.stop_service(
            service_uuid,
            user_id=user_id,
            is_admin=is_admin
        )
        if not result:
            err_msg = "停止服务失败，服务可能不存在"
            return error_response(err_msg, code=400, http_status_code=400)

        return success_response({"message": "服务已停止"})
    except ValueError as e:
        # 权限错误
        return error_response(str(e), code=403, http_status_code=403)
    except Exception as e:
        mcp_logger.error(f"停止服务失败: {str(e)}")
        return error_response(
            f"停止服务失败: {str(e)}", code=500, http_status_code=500
        )


async def start_service(request: Request):
    """启动服务"""
    service_uuid = request.path_params["service_uuid"]

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    try:
        # 启动服务
        result = service_manager.start_service(
            service_uuid,
            user_id=user_id,
            is_admin=is_admin
        )
        if not result:
            err_msg = "启动服务失败，服务可能不存在"
            return error_response(err_msg, code=400, http_status_code=400)

        return success_response({"message": "服务已启动"})
    except Exception as e:
        mcp_logger.error(f"启动服务失败: {str(e)}")
        err_msg = f"启动服务失败: {str(e)}"
        return error_response(err_msg, code=500, http_status_code=500)


async def uninstall_service(request: Request):
    """卸载服务"""
    service_uuid = request.path_params["service_uuid"]

    # 获取用户信息
    user_id, is_admin = get_user_info(request)

    try:
        # 删除服务
        result = service_manager.delete_service(
            service_uuid,
            user_id=user_id,
            is_admin=is_admin
        )
        if not result:
            err_msg = "卸载服务失败，服务可能不存在"
            return error_response(err_msg, code=400, http_status_code=400)

        return success_response({"message": "服务已卸载"})
    except Exception as e:
        mcp_logger.error(f"卸载服务失败: {str(e)}")
        return error_response(
            f"卸载服务失败: {str(e)}", code=500, http_status_code=500
        )


async def update_service_description(request: Request):
    """更新服务描述"""
    service_uuid = request.path_params["service_uuid"]
    
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    try:
        data = await request.json()
        description = data.get("description", "")

        # 调用service_manager更新描述
        success = service_manager.update_service_description(
            service_uuid=service_uuid,
            description=description,
            user_id=user_id,
            is_admin=is_admin
        )
        
        if success:
            return success_response(message="服务说明已更新")
        else:
            return error_response(
                "更新服务说明失败", code=500, http_status_code=500
            )
            
    except ValueError as e:
        return error_response(str(e), code=400, http_status_code=400)
    except Exception as e:
        mcp_logger.error(f"更新服务说明失败: {str(e)}")
        return error_response(
            f"更新服务说明失败: {str(e)}", code=500, http_status_code=500
        )


async def update_service_visibility(request: Request):
    """更新服务公开/私有状态"""
    id = request.path_params["id"]
    
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    try:
        data = await request.json()
        is_public = data.get("is_public")
        
        if is_public is None:
            return error_response(
                "缺少is_public参数", code=400, http_status_code=400
            )
        
        # 调用service_manager更新可见性
        result = service_manager.update_service_visibility(
            id=id,
            is_public=is_public,
            user_id=user_id,
            is_admin=is_admin
        )
        
        visibility_text = "公开" if result["is_public"] else "私有"
        return success_response(
            result, 
            message=f"服务已设置为{visibility_text}"
        )
            
    except ValueError as e:
        return error_response(str(e), code=400, http_status_code=400)
    except Exception as e:
        mcp_logger.error(f"更新服务可见性失败: {str(e)}")
        return error_response(
            f"更新服务可见性失败: {str(e)}", code=500, http_status_code=500
        )


async def list_modules_for_select(request: Request):
    """获取模块列表用于下拉选择器"""
    try:
        # 获取用户信息
        user_id, is_admin = get_user_info(request)

        # 调用service_manager获取模块列表
        result = service_manager.get_modules_for_select(
            user_id=user_id,
            is_admin=is_admin
        )

        return success_response(result)
    except Exception as e:
        mcp_logger.error(f"获取模块列表失败: {str(e)}")
        return error_response(
            f"获取模块列表失败: {str(e)}", code=500, http_status_code=500
        )


async def list_users_for_select(request: Request):
    """获取用户列表用于下拉选择器"""
    try:
        # 获取用户信息
        user_id, is_admin = get_user_info(request)

        # 调用service_manager获取用户列表
        result = service_manager.get_users_for_select(
            user_id=user_id,
            is_admin=is_admin
        )

        return success_response(result)
    except ValueError as e:
        return error_response(str(e), code=403, http_status_code=403)
    except Exception as e:
        mcp_logger.error(f"获取用户列表失败: {str(e)}")
        return error_response(
            f"获取用户列表失败: {str(e)}", code=500, http_status_code=500
        )


def get_router():
    """获取MCP服务路由"""
    routes = [
        Route("/load_tool", endpoint=load_tool, methods=["POST"]),
        Route("/unload_tool", endpoint=unload_tool, methods=["POST"]),
        Route("/restart", endpoint=restart_service, methods=["POST"]),
        Route("/status", endpoint=get_status, methods=["GET"]),
        Route("/enabled_tools", endpoint=enabled_tools, methods=["GET"]),
        Route("/{id:int}/params", endpoint=update_params, methods=["PUT"]),

        # 从marketplace.py迁移过来的服务相关路由
        # 注意：静态路由必须放在动态路由之前，避免路由冲突
        Route("/online", get_online_services, methods=["GET"]),
        Route("/list", list_services, methods=["GET"]),
        Route("/page", page_services, methods=["POST"]),
        Route("/{service_uuid}", get_service, methods=["GET"]),
        Route("/{service_uuid}/stop", stop_service, methods=["POST"]),
        Route("/{service_uuid}/start", start_service, methods=["POST"]),
        Route("/{service_uuid}/uninstall", uninstall_service,
              methods=["POST"]),
        Route("/{service_uuid}/description", update_service_description,
              methods=["PUT"]),
        Route("/{id}/visibility", update_service_visibility,
              methods=["PUT"]),
        Route("/modules_for_select", list_modules_for_select, methods=["GET"]),
        Route("/users_for_select", list_users_for_select, methods=["GET"]),
        # 第三方服务管理
        Route("/third-party-services", create_third_party_service, methods=["POST"]),
    ]

    return routes
