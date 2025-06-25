"""
统计数据定时任务

定期更新系统中各种统计数据
"""

import time
import threading
import schedule
from datetime import datetime, date, timedelta
from pytz import timezone

from app.core.config import settings
from app.services.statistics.service import statistics_service
from app.utils.logging import mcp_logger


# 默认统计任务间隔（分钟）
DEFAULT_STATISTICS_INTERVAL = 60

# 默认历史数据保留天数
DEFAULT_HISTORY_RETENTION_DAYS = 90


# 从配置中获取统计任务间隔，如果没有配置则使用默认值
def get_statistics_interval():
    """获取统计任务间隔时间（分钟）"""
    try:
        return settings.STATISTICS_INTERVAL
    except Exception:
        return DEFAULT_STATISTICS_INTERVAL


def get_history_retention_days():
    """获取历史数据保留天数"""
    try:
        return settings.STATISTICS_HISTORY_RETENTION_DAYS
    except Exception:
        return DEFAULT_HISTORY_RETENTION_DAYS


def update_daily_statistics():
    """
    更新每日统计数据
    
    确保今日的统计数据是最新的
    """
    try:
        tz = timezone('Asia/Shanghai')
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        mcp_logger.info(f"开始执行每日统计数据更新任务: {current_time}")
        
        # 更新今日统计
        stats = statistics_service.update_service_statistics()
        mcp_logger.info(
            f"今日统计数据更新完成: 模板分组 {stats.total_template_groups}, "
            f"模板 {stats.total_templates}, 工具调用 {stats.total_tools_calls}"
        )
        
        # 刷新其他统计表
        result = statistics_service.refresh_all_statistics()
        mcp_logger.info(f"其他统计数据更新完成: {result}")
        
    except Exception as e:
        mcp_logger.error(f"执行每日统计数据更新任务出错: {str(e)}")


def update_statistics():
    """
    更新所有统计数据
    
    调用统计服务的刷新方法，更新所有统计表数据
    """
    try:
        tz = timezone('Asia/Shanghai')
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        mcp_logger.info(f"开始执行统计数据定时更新任务: {current_time}")
        
        # 更新每日统计
        update_daily_statistics()
        
    except Exception as e:
        mcp_logger.error(f"执行统计数据定时更新任务出错: {str(e)}")


def clean_old_statistics():
    """
    清理过期的统计数据
    
    删除超过保留期限的历史统计数据
    """
    try:
        from app.models.engine import get_db
        from app.models.statistics import ServiceStatistics
        
        retention_days = get_history_retention_days()
        cutoff_date = date.today() - timedelta(days=retention_days)
        
        tz = timezone('Asia/Shanghai')
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        mcp_logger.info(f"开始清理 {cutoff_date} 之前的统计数据: {current_time}")
        
        with get_db() as db:
            deleted_count = db.query(ServiceStatistics).filter(
                ServiceStatistics.statistics_date < cutoff_date
            ).delete()
            db.commit()
            
            if deleted_count > 0:
                mcp_logger.info(f"已清理 {deleted_count} 条过期统计数据")
            else:
                mcp_logger.info("没有需要清理的过期统计数据")
                
    except Exception as e:
        mcp_logger.error(f"清理过期统计数据时出错: {str(e)}")


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
    
    # 设置统计数据更新定时任务
    schedule.every(interval).minutes.do(update_statistics)
    
    # 设置每日凌晨清理过期数据任务
    schedule.every().day.at("01:00").do(clean_old_statistics)
    
    # 设置每日定时统计任务（确保每天的数据都能更新）
    schedule.every().day.at("23:55").do(update_daily_statistics)
    
    # 在单独的线程中运行调度器
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    mcp_logger.info("统计数据定时任务已成功启动")
    mcp_logger.info(f"历史数据保留天数: {get_history_retention_days()}天")
    
    return scheduler_thread 