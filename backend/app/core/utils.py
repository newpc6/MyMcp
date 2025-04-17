"""
工具函数模块
"""
from datetime import datetime, timedelta


def now_beijing():
    """获取北京时间（UTC+8）的当前时间函数
    
    用于数据库模型的默认时间，替代func.now()
    """
    def _beijing_time():
        return datetime.utcnow() + timedelta(hours=8)
    
    return _beijing_time 