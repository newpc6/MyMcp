"""
示例工具模块，演示如何不通过装饰器而是通过代码动态注册MCP工具
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from repository.mcp_base import add_tool, mcp


def add_numbers(numbers: List[int]) -> int:
    """
    求和函数，演示简单工具
    """
    if not numbers:
        return 0
        
    return sum(numbers)


def search_records(
    query: str,
    limit: int = 10,
    include_details: bool = False
) -> List[Dict[str, Any]]:
    """
    搜索记录的示例工具
    
    Args:
        query: 搜索关键词
        limit: 返回结果限制数量
        include_details: 是否包含详细信息
        
    Returns:
        List[Dict[str, Any]]: 搜索结果列表
    """
    # 模拟搜索结果
    results = []
    for i in range(1, limit + 1):
        record = {
            "id": f"rec_{i}",
            "title": f"记录 {i} - 包含 {query}",
            "score": round(0.9 - (i * 0.05), 2)
        }
        
        # 如果需要详细信息，添加额外字段
        if include_details:
            record["details"] = {
                "created_at": "2023-10-10T10:00:00",
                "author": "系统",
                "category": "示例"
            }
        
        results.append(record)
    
    return results


def create_record(
    title: str,
    content: str,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    创建记录的示例工具
    
    Args:
        title: 记录标题
        content: 记录内容
        tags: 标签列表
        
    Returns:
        Dict[str, Any]: 创建结果
    """
    # 模拟创建记录
    record_id = "rec_" + str(hash(title + content))[0:8]
    
    return {
        "success": True,
        "record_id": record_id,
        "title": title,
        "content_length": len(content),
        "tags": tags or [],
        "created_at": "2023-10-10T10:00:00"
    }


# 这里不需要使用装饰器，可以通过代码来动态注册工具
# 可以通过前端界面来动态加载，或者在模块导入时就添加

# 如果想要在模块导入时就添加这些工具，可以取消下面的注释
# add_tool(search_records, "search_records", "搜索记录工具")
# add_tool(create_record, "create_record", "创建记录工具") 