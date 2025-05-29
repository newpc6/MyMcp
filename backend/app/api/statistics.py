"""
统计API路由

提供MCP服务和工具调用统计数据的REST接口
"""

from starlette.routing import Route
from starlette.requests import Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.services.statistics.service import statistics_service
from app.utils.response import success_response, error_response
from app.utils.logging import mcp_logger
from app.utils.http import get_page_params

async def get_service_statistics(request: Request):
    """获取服务统计数据"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        stats = statistics_service.get_service_statistics()
        return success_response(stats)
    except Exception as e:
        return error_response(
            f"获取服务统计失败: {str(e)}",
            code=500, 
            http_status_code=500
        )


async def get_module_rankings(request: Request):
    """获取模块发布排名"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        # 使用通用分页工具获取分页参数
        page_params = get_page_params(request)
        
        result = statistics_service.get_module_rankings(
            size=page_params.size, 
            page=page_params.page
        )
        return success_response(result)
    except Exception as e:
        return error_response(
            f"获取模块排名失败: {str(e)}",
            code=500, 
            http_status_code=500
        )


async def get_tool_rankings(request: Request):
    """获取工具调用排名"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        # 使用通用分页工具获取分页参数
        page_params = get_page_params(request)
        
        result = statistics_service.get_tool_rankings(
            size=page_params.size, 
            page=page_params.page
        )
        return success_response(result)
    except Exception as e:
        return error_response(
            f"获取工具排名失败: {str(e)}",
            code=500, 
            http_status_code=500
        )


async def get_service_rankings(request: Request):
    """获取服务调用排名"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        # 使用通用分页工具获取分页参数
        page_params = get_page_params(request)
        
        result = statistics_service.get_service_rankings(
            size=page_params.size, 
            page=page_params.page
        )
        return success_response(result)
    except Exception as e:
        return error_response(
            f"获取服务调用排名失败: {str(e)}",
            code=500, 
            http_status_code=500
        )


async def get_tool_executions(request: Request):
    """获取工具执行记录"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        # 使用通用分页工具获取分页参数
        page_params = get_page_params(request)
        
        # 获取其他过滤参数
        tool_name = request.query_params.get("tool_name")
        
        data = statistics_service.get_tool_executions(
            page=page_params.page,
            size=page_params.size,
            tool_name=tool_name
        )
        return success_response(data)
    except Exception as e:
        mcp_logger.error(f"获取工具执行记录时出错: {str(e)}")
        return error_response(str(e))


async def refresh_statistics(request: Request):
    """刷新统计数据"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        result = statistics_service.refresh_all_statistics()
        return success_response({
            "message": "统计数据已刷新",
            "details": result
        })
    except Exception as e:
        mcp_logger.error(f"刷新统计数据时出错: {str(e)}")
        return error_response(str(e))


async def get_tool_executions_by_module(request: Request):
    """获取按模块分组的工具执行记录"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        # 使用通用分页工具获取分页参数
        page_params = get_page_params(request)
        
        # 获取其他过滤参数
        module_id = request.query_params.get("module_id")
        
        # 转换module_id参数类型
        try:
            module_id = int(module_id) if module_id else None
        except ValueError:
            module_id = None
        
        data = statistics_service.get_tool_executions_by_module(
            page=page_params.page,
            size=page_params.size,
            module_id=module_id
        )
        return success_response(data)
    except Exception as e:
        mcp_logger.error(f"获取模块工具执行记录时出错: {str(e)}")
        return error_response(str(e))


async def get_tool_executions_by_service(request: Request):
    """获取按服务分组的工具执行记录"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        # 使用通用分页工具获取分页参数
        page_params = get_page_params(request)
        
        # 获取其他过滤参数
        service_id = request.query_params.get("service_id")
        
        data = statistics_service.get_tool_executions_by_service(
            page=page_params.page,
            size=page_params.size,
            service_id=service_id
        )
        return success_response(data)
    except Exception as e:
        mcp_logger.error(f"获取服务工具执行记录时出错: {str(e)}")
        return error_response(str(e))


async def get_module_tool_rankings(request: Request):
    """获取特定模块的工具调用排名"""
    try:
        # 检查管理员权限
        user = request.state.user
        if not user.get("is_admin", False):
            return error_response(
                "需要管理员权限", 
                code=403, 
                http_status_code=403
            )
        
        # 从路径中获取模块ID
        module_id = request.path_params.get("module_id")
        
        # 获取查询参数
        
        # 转换参数类型
        try:
            module_id = int(module_id)
        except (ValueError, TypeError):
            return error_response(
                "无效的模块ID", 
                code=400, 
                http_status_code=400
            )
        
        page_params = get_page_params(request)
        size = page_params.size
        
        data = statistics_service.get_module_tool_rankings(
            module_id=module_id,
            limit=size
        )
        return success_response(data)
    except Exception as e:
        mcp_logger.error(f"获取模块工具排名时出错: {str(e)}")
        return error_response(str(e))


def get_router():
    """获取统计API路由"""
    routes = [
        Route("/services", endpoint=get_service_statistics, methods=["GET"]),
        Route("/modules/rankings", endpoint=get_module_rankings, methods=["GET"]),
        Route("/tools/rankings", endpoint=get_tool_rankings, methods=["GET"]),
        Route("/services/rankings", endpoint=get_service_rankings, methods=["GET"]),
        Route("/tools/executions", endpoint=get_tool_executions, methods=["GET"]),
        Route("/refresh", endpoint=refresh_statistics, methods=["POST"]),
        Route(
            "/tools/executions/by-module", 
            endpoint=get_tool_executions_by_module, 
            methods=["GET"]
        ),
        Route(
            "/tools/executions/by-service", 
            endpoint=get_tool_executions_by_service, 
            methods=["GET"]
        ),
        Route(
            "/modules/{module_id}/tool-rankings", 
            endpoint=get_module_tool_rankings, 
            methods=["GET"]
        )
    ]
    
    return routes 