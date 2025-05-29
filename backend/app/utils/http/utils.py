"""
HTTP通用工具函数

提供HTTP相关的通用工具函数
"""
from fastapi import Request
from typing import Callable, List, Any, Dict

from .pagination import PageParams


def body_page_params(
    body: dict, 
    default_size: int = 10, 
    max_size: int = 50
) -> PageParams:
    """
    获取分页参数
    """
    return PageParams.from_request_body(body, default_size, max_size)


def get_page_params(
    request: Request, 
    default_size: int = 10, 
    max_size: int = 50
) -> PageParams:
    """
    获取分页参数
    
    Args:
        request: FastAPI请求对象
        default_size: 默认每页条数
        max_size: 最大每页条数
        
    Returns:
        PageParams: 分页参数对象
    """
    return PageParams.from_request(request, default_size, max_size)


def get_page_body(
    request: Request, 
    default_size: int = 10, 
    max_size: int = 50
) -> PageParams:
    """
    获取分页参数
    """

def paginate_dependency(
    default_size: int = 10, 
    max_size: int = 50
) -> Callable:
    """
    创建分页参数依赖项
    
    用法:
    ```
    @app.get("/items")
    async def list_items(
        page_params: PageParams = Depends(paginate_dependency())
    ):
        # 使用page_params.page, page_params.limit, page_params.offset
        pass
    ```
    
    Args:
        default_size: 默认每页条数
        max_size: 最大每页条数
        
    Returns:
        Callable: FastAPI依赖函数
    """
    def _get_page_params(
        page: int = 1, 
        size: int = default_size
    ) -> PageParams:
        # 验证和处理分页参数
        if page < 1:
            page = 1
            
        if size < 1:
            size = default_size
        elif size > max_size:
            size = max_size
            
        offset = (page - 1) * size
        return PageParams(page=page, size=size, offset=offset)
    
    return _get_page_params 


def build_page_response(
    items: List[Any],
    total: int, 
    page_params: PageParams
) -> Dict[str, Any]:
    """
    构建统一的分页响应结果
    
    Args:
        items: 数据项列表
        total: 总数量
        page_params: 分页参数
        
    Returns:
        Dict: 统一格式的分页响应
    """    
    return {
        "items": items,
        "total": total,
        "page": page_params.page,
        "size": page_params.size
    }
