"""
定时任务模块

提供系统各种定时任务的功能
"""

from .statistics_task import start_statistics_scheduler

__all__ = ["start_statistics_scheduler"] 