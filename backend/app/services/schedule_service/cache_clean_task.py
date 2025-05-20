"""
缓存清理定时任务模块
"""
from app.utils.cache import memory_cache
from app.utils.logging import em_logger


def clean_expired_cache() -> None:
    """清理过期的缓存数据"""
    try:
        count = memory_cache.clean_expired()
        if count > 0:
            em_logger.info(f"定时清理了 {count} 个过期缓存项")
    except Exception as e:
        em_logger.error(f"清理缓存失败: {str(e)}") 