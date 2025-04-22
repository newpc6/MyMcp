from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from ..services.history.service import HistoryService

history_service = HistoryService()


async def get_executions(request: Request):
    """获取工具调用记录，支持分页和搜索"""
    params = request.query_params
    page = int(params.get("page", "1"))
    page_size = int(params.get("page_size", "10"))
    tool_name = params.get("tool_name")
    
    result = history_service.get_executions(page, page_size, tool_name)
    return JSONResponse(result)


async def get_recent_activities(request: Request):
    """获取最近的活动记录"""
    params = request.query_params
    limit = int(params.get("limit", "10"))
    
    result = history_service.get_recent_activities(limit)
    return JSONResponse(result)


async def get_execution_stats(request: Request):
    """获取执行统计数据"""
    result = {
        "execution_count": history_service.get_execution_count(),
        "last_execution_time": history_service.get_last_execution_time()
    }
    return JSONResponse(result)


def get_router():
    """获取历史记录路由"""
    routes = [
        Route("/executions", endpoint=get_executions, methods=["GET"]),
        Route("/activities", endpoint=get_recent_activities, methods=["GET"]),
        Route("/stats", endpoint=get_execution_stats, methods=["GET"])
    ]
    
    return routes 