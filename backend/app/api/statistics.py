"""
统计API路由

提供MCP服务和工具调用统计数据的REST接口
"""

from starlette.routing import Route
from starlette.requests import Request
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.services.statistics.service import statistics_service
from app.utils.response import success_response, error_response
from app.utils.logging import em_logger

class LimitRequest(BaseModel):
    """排名限制请求模型"""
    limit: int = 10


class PaginationRequest(BaseModel):
    """分页请求模型"""
    page: int = 1
    per_page: int = 20
    tool_name: Optional[str] = None


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
        
        # 获取查询参数
        limit = request.query_params.get("limit", "10")
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
            elif limit > 50:
                limit = 50
        except ValueError:
            limit = 10
        
        rankings = statistics_service.get_module_rankings(limit=limit)
        return success_response(rankings)
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
        
        # 获取查询参数
        limit = request.query_params.get("limit", "10")
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
            elif limit > 50:
                limit = 50
        except ValueError:
            limit = 10
        
        rankings = statistics_service.get_tool_rankings(limit=limit)
        return success_response(rankings)
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
        
        # 获取查询参数
        limit = request.query_params.get("limit", "10")
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
            elif limit > 50:
                limit = 50
        except ValueError:
            limit = 10
        
        rankings = statistics_service.get_service_rankings(limit=limit)
        return success_response(rankings)
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
        
        # 获取查询参数
        params = request.query_params
        page = params.get("page", "1")
        per_page = params.get("per_page", "20")
        tool_name = params.get("tool_name")
        
        # 转换参数类型
        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        
        try:
            per_page = int(per_page)
            if per_page < 1:
                per_page = 20
            elif per_page > 100:
                per_page = 100
        except ValueError:
            per_page = 20
        
        data = statistics_service.get_tool_executions(
            page=page,
            per_page=per_page,
            tool_name=tool_name
        )
        return success_response(data)
    except Exception as e:
        em_logger.error(f"获取工具执行记录时出错: {str(e)}")
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
        em_logger.error(f"刷新统计数据时出错: {str(e)}")
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
        
        # 获取查询参数
        params = request.query_params
        page = params.get("page", "1")
        per_page = params.get("per_page", "20")
        module_id = params.get("module_id")
        
        # 转换参数类型
        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        
        try:
            per_page = int(per_page)
            if per_page < 1:
                per_page = 20
            elif per_page > 100:
                per_page = 100
        except ValueError:
            per_page = 20
        
        try:
            module_id = int(module_id) if module_id else None
        except ValueError:
            module_id = None
        
        data = statistics_service.get_tool_executions_by_module(
            page=page,
            per_page=per_page,
            module_id=module_id
        )
        return success_response(data)
    except Exception as e:
        em_logger.error(f"获取模块工具执行记录时出错: {str(e)}")
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
        
        # 获取查询参数
        params = request.query_params
        page = params.get("page", "1")
        per_page = params.get("per_page", "20")
        service_id = params.get("service_id")
        
        # 转换参数类型
        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        
        try:
            per_page = int(per_page)
            if per_page < 1:
                per_page = 20
            elif per_page > 100:
                per_page = 100
        except ValueError:
            per_page = 20
        
        data = statistics_service.get_tool_executions_by_service(
            page=page,
            per_page=per_page,
            service_id=service_id
        )
        return success_response(data)
    except Exception as e:
        em_logger.error(f"获取服务工具执行记录时出错: {str(e)}")
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
        limit = request.query_params.get("limit", "10")
        
        # 转换参数类型
        try:
            module_id = int(module_id)
        except (ValueError, TypeError):
            return error_response(
                "无效的模块ID", 
                code=400, 
                http_status_code=400
            )
            
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
            elif limit > 50:
                limit = 50
        except ValueError:
            limit = 10
        
        data = statistics_service.get_module_tool_rankings(
            module_id=module_id,
            limit=limit
        )
        return success_response(data)
    except Exception as e:
        em_logger.error(f"获取模块工具排名时出错: {str(e)}")
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