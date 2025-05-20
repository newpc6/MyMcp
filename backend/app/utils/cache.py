"""
缓存工具模块

提供内存缓存功能，用于存储临时数据（如第三方平台授权信息）
"""
from typing import Dict, Any, Optional
import time
import threading


class MemoryCache:
    """内存缓存类，用于存储临时数据"""
    
    def __init__(self):
        """初始化缓存"""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire_seconds: 过期时间（秒）
        """
        with self._lock:
            expire_at = (time.time() + expire_seconds 
                        if expire_seconds > 0 else 0)
            self._cache[key] = {
                "value": value,
                "expire_at": expire_at
            }
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        with self._lock:
            if key not in self._cache:
                return None
                
            cache_item = self._cache[key]
            
            # 检查是否过期
            if (cache_item["expire_at"] > 0 and 
                cache_item["expire_at"] < time.time()):
                # 已过期，删除缓存
                del self._cache[key]
                return None
                
            return cache_item["value"]
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            
    def clean_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的缓存数量
        """
        count = 0
        current_time = time.time()
        
        with self._lock:
            keys_to_delete = []
            
            for key, cache_item in self._cache.items():
                if (cache_item["expire_at"] > 0 and 
                    cache_item["expire_at"] < current_time):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._cache[key]
                count += 1
                
        return count


# 全局缓存实例
memory_cache = MemoryCache() 