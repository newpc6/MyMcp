from starlette.routing import Route
from starlette.requests import Request
from app.utils.response import success_response, error_response

from ..models.tools.schemas import (
    ToolCreate, ToolUpdate
)
from ..services.tools.service import ToolService
from app.core.config import settings

tool_service = ToolService()


async def get_tools(request: Request):
    """获取所有工具信息"""
    result = tool_service.get_all_tools()
    return success_response(result)


async def list_tools(request: Request):
    """获取所有工具信息列表"""
    result = tool_service.list_tools()
    return success_response(result)


async def get_tool_info(request: Request):
    """获取特定工具信息"""
    tool_name = request.path_params["tool_name"]
    try:
        result = tool_service.get_tool_info(tool_name)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), code=404, http_status_code=404)


async def get_tool(request: Request):
    """获取工具内容"""
    tool_path = request.path_params["tool_path"]
    try:
        result = tool_service.get_tool_content(tool_path)
        return success_response(result)
    except FileNotFoundError:
        return error_response("工具未找到", code=404, http_status_code=404)
    except PermissionError:
        return error_response("没有权限访问该工具", code=403, http_status_code=403)
    except Exception as e:
        error_msg = f"获取工具内容失败: {str(e)}"
        return error_response(error_msg, code=500, http_status_code=500)


async def update_tool(request: Request):
    """更新工具内容"""
    tool_path = request.path_params["tool_path"]
    try:
        data = await request.json()
        tool_update = ToolUpdate(**data)
        
        tool_service.update_tool(tool_path, tool_update.content)
        return success_response(message="工具更新成功")
    except FileNotFoundError:
        return error_response("工具未找到", code=404, http_status_code=404)


async def create_tool(request: Request):
    """创建新工具"""
    try:
        data = await request.json()
        tool_create = ToolCreate(**data)
        
        tool_service.create_tool(tool_create.path, tool_create.content)
        return success_response(message="工具创建成功")
    except FileExistsError:
        return error_response("工具已存在", code=409, http_status_code=409)


async def delete_tool(request: Request):
    """删除工具"""
    tool_path = request.path_params["tool_path"]
    try:
        tool_service.delete_tool(tool_path)
        return success_response(message="工具删除成功")
    except FileNotFoundError:
        return error_response("工具未找到", code=404, http_status_code=404)


def get_router():
    """获取工具路由"""
    routes = [
        Route("/", endpoint=get_tools, methods=["GET"]),
        Route("/list", endpoint=list_tools, methods=["GET"]),
        Route("/info/{tool_name}", endpoint=get_tool_info, methods=["GET"]),
        Route("/{tool_path:path}", endpoint=get_tool, methods=["GET"]),
        Route("/{tool_path:path}", endpoint=update_tool, methods=["PUT"]),
        Route("/", endpoint=create_tool, methods=["POST"]),
        Route("/{tool_path:path}", endpoint=delete_tool, methods=["DELETE"])
    ]
    
    return routes 