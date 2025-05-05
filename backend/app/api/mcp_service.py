from starlette.routing import Route
from starlette.requests import Request
from pydantic import BaseModel, ValidationError
import importlib

from app.utils.response import success_response, error_response
from app.server.mcp_server import (
    add_tool, remove_tool, restart_mcp_server, check_mcp_status, get_enabled_tools, update_service_params
)
from ..core.config import settings


class ToolLoadRequest(BaseModel):
    """加载工具请求模型"""
    module_path: str  # 模块路径，例如 "repository.demo_tool"
    function_name: str  # 函数名称
    tool_name: str = None  # 可选的工具名称，默认使用函数名
    description: str = None  # 可选的工具描述


class ToolRemoveRequest(BaseModel):
    """移除工具请求模型"""
    tool_name: str  # 工具名称


class UpdateSSEUrlRequest(BaseModel):
    """更新SSE URL请求模型"""
    sse_url: str  # 新的SSE URL


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
        return error_response(f"加载工具失败: {str(e)}", code=500, http_status_code=500)


async def unload_tool(request: Request):
    """动态卸载工具"""
    try:
        data = await request.json()
        request_data = ToolRemoveRequest(**data)
        
        success = remove_tool(request_data.tool_name)
        if success:
            return success_response(message=f"工具 {request_data.tool_name} 已成功卸载")
        else:
            error_msg = f"工具 {request_data.tool_name} 不存在或卸载失败"
            return error_response(error_msg, code=404, http_status_code=404)
    except ValidationError as e:
        return error_response(str(e), code=422, http_status_code=422)
    except Exception as e:
        return error_response(f"卸载工具失败: {str(e)}", code=500, http_status_code=500)


async def restart_service(request: Request):
    """重启MCP服务"""
    try:
        success = restart_mcp_server()
        if success:
            return success_response(message="MCP服务已成功重启")
        else:
            return error_response("MCP服务重启失败", code=500, http_status_code=500)
    except Exception as e:
        return error_response(f"重启服务失败: {str(e)}", code=500, http_status_code=500)


async def get_status(request: Request):
    """获取MCP服务状态"""
    try:
        status = check_mcp_status()
        return success_response(status)
    except Exception as e:
        return error_response(f"获取服务状态失败: {str(e)}", code=500, http_status_code=500)


async def enabled_tools(request: Request):
    """获取当前启用的工具列表"""
    try:
        tools_list = get_enabled_tools()
        return success_response({
            "enabled_tools": tools_list, 
            "count": len(tools_list)
        })
    except Exception as e:
        error_msg = f"获取启用工具列表失败: {str(e)}"
        return error_response(error_msg, code=500, http_status_code=500)


async def update_sse_url(request: Request):
    """更新MCP SSE URL"""
    try:
        data = await request.json()
        request_data = UpdateSSEUrlRequest(**data)
        
        # 更新配置
        settings.MCP_SSE_URL = request_data.sse_url
        
        # 返回更新后的状态
        return success_response({
            "new_sse_url": settings.MCP_SSE_URL
        }, message="MCP SSE URL已更新")
    except ValidationError as e:
        return error_response(str(e), code=422, http_status_code=422)
    except Exception as e:
        return error_response(f"更新SSE URL失败: {str(e)}", code=500, http_status_code=500)


async def update_params(request: Request):
    """更新服务参数"""
    try:
        data = await request.json()
        id = request.path_params["id"]
        # 更新服务参数
        update_service_params(id, data)

        return success_response(message="服务参数更新成功")
    except Exception as e:
        return error_response(f"更新服务参数失败: {str(e)}", code=500, http_status_code=500)

def get_router():
    """获取MCP服务路由"""
    routes = [
        Route("/load_tool", endpoint=load_tool, methods=["POST"]),
        Route("/unload_tool", endpoint=unload_tool, methods=["POST"]),
        Route("/restart", endpoint=restart_service, methods=["POST"]),
        Route("/status", endpoint=get_status, methods=["GET"]),
        Route("/enabled_tools", endpoint=enabled_tools, methods=["GET"]),
        Route("/sse_url", endpoint=update_sse_url, methods=["PUT"]),
        Route("/{id:int}/params", endpoint=update_params, methods=["PUT"])
    ]
    
    return routes 