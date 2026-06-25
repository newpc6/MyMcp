"""定时任务服务规范入口。"""
from app.services.schedule_service import (
    start_cache_clean_scheduler,
    start_statistics_scheduler,
)
from app.services.schedule_service.cache_clean_task import clean_expired_cache
from app.services.schedule_service.statistics_task import (
    clean_old_statistics,
    update_daily_statistics,
    update_statistics,
)

__all__ = [
    "start_cache_clean_scheduler",
    "start_statistics_scheduler",
    "clean_expired_cache",
    "update_daily_statistics",
    "update_statistics",
    "clean_old_statistics",
]
