"""
统计数据定时任务

定期更新系统中各种统计数据
"""

import time
import threading
import schedule
from datetime import datetime
from pytz import timezone

from app.core.config import settings
from app.services.statistics.service import statistics_service
from app.utils.logging import mcp_logger


# 默认统计任务间隔（分钟）
DEFAULT_STATISTICS_INTERVAL = 60


# 从配置中获取统计任务间隔，如果没有配置则使用默认值
def get_statistics_interval():
    """获取统计任务间隔时间（分钟）"""
    try:
        return settings.STATISTICS_INTERVAL
    except Exception:
        return DEFAULT_STATISTICS_INTERVAL


def update_statistics():
    """
    更新所有统计数据
    
    调用统计服务的刷新方法，更新所有统计表数据
    """
    try:
        tz = timezone('Asia/Shanghai')
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        mcp_logger.info(f"开始执行统计数据定时更新任务: {current_time}")
        result = statistics_service.refresh_all_statistics()
        mcp_logger.info(f"统计数据更新完成: {result}")
    except Exception as e:
        mcp_logger.error(f"执行统计数据定时更新任务出错: {str(e)}")


def run_scheduler():
    """
    运行定时任务调度器
    
    持续运行调度器，防止程序退出
    """
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_statistics_scheduler():
    """
    启动统计数据定时任务
    
    根据配置的间隔时间，定期执行统计数据更新任务
    """
    interval = get_statistics_interval()
    mcp_logger.info(f"启动统计数据定时更新任务，间隔时间: {interval}分钟")
    
    # 设置定时任务
    schedule.every(interval).minutes.do(update_statistics)
    
    # 立即执行一次
    update_statistics()
    
    # 在单独的线程中运行调度器
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    mcp_logger.info("统计数据定时任务已成功启动")
    
    return scheduler_thread 