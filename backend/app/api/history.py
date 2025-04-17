from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional

from ..services.history.service import HistoryService

router = APIRouter()
history_service = HistoryService()


@router.get("/executions", response_model=Dict[str, Any])
async def get_executions(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页记录数"),
    tool_name: Optional[str] = Query(None, description="工具名称，用于搜索过滤")
):
    """获取工具调用记录，支持分页和搜索"""
    return history_service.get_executions(page, page_size, tool_name)


@router.get("/activities", response_model=List[Dict[str, Any]])
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=100)
):
    """获取最近的活动记录"""
    return history_service.get_recent_activities(limit)


@router.get("/stats", response_model=Dict[str, Any])
async def get_execution_stats():
    """获取执行统计数据"""
    return {
        "execution_count": history_service.get_execution_count(),
        "last_execution_time": history_service.get_last_execution_time()
    } 