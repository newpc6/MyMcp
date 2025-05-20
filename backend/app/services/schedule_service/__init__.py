"""
定时任务模块

提供系统各种定时任务的功能
"""
import schedule
import time
import threading

from .statistics_task import start_statistics_scheduler
from .cache_clean_task import clean_expired_cache

# 每小时运行一次缓存清理任务
schedule.every(1).hour.do(clean_expired_cache)


def start_cache_clean_scheduler():
    """启动缓存清理定时任务"""
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    # 在后台线程中运行定时器
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()


__all__ = [
    "start_statistics_scheduler",
    "start_cache_clean_scheduler"
] 