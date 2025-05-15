"""
分页参数处理工具

提供通用的分页参数处理功能，包括分页参数获取、验证和分页数据封装
"""
from typing import Dict, Any, List, TypeVar, Generic
from fastapi import Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Query as SQLAQuery

T = TypeVar('T')


class PageParams(BaseModel):
    """分页参数模型"""
    page: int
    size: int
    offset: int
    
    @classmethod
    def from_request(
        cls, request: Request, default_size: int = 10, max_size: int = 50
    ) -> 'PageParams':
        """
        从请求中提取分页参数
        
        Args:
            request: FastAPI请求对象
            default_size: 默认每页条数
            max_size: 最大每页条数
            
        Returns:
            PageParams: 分页参数对象
        """
        params = request.query_params
        size_str = params.get("size", str(default_size))
        page_str = params.get("page", "1")
        
        try:
            size = int(size_str)
            if size < 1:
                size = default_size
            elif size > max_size:
                size = max_size
        except ValueError:
            size = default_size
            
        try:
            page = int(page_str)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
            
        offset = (page - 1) * size
        
        return cls(page=page, size=size, offset=offset)
    
    @classmethod
    def from_params(
        cls, 
        page: int = Query(1, ge=1, description="页码，从1开始"), 
        size: int = Query(10, ge=1, le=50, description="每页条数")
    ) -> 'PageParams':
        """
        从FastAPI查询参数中提取分页参数
        
        Args:
            page: 页码参数
            size: 每页条数参数
            
        Returns:
            PageParams: 分页参数对象
        """
        offset = (page - 1) * size
        return cls(page=page, size=size, offset=offset)


class PageResult(Generic[T], BaseModel):
    """分页结果模型"""
    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int
    
    @classmethod
    def from_query(
        cls, query: SQLAQuery, page_params: PageParams, items=None
    ) -> 'PageResult':
        """
        从SQLAlchemy查询对象创建分页结果
        
        Args:
            query: SQLAlchemy查询对象
            page_params: 分页参数
            items: 如果已经查询过结果，可以直接提供
            
        Returns:
            PageResult: 分页结果对象
        """
        # 获取总数
        total_count = query.count()
        
        # 如果没有提供items，则执行查询
        if items is None:
            items = query.offset(page_params.offset).limit(page_params.size).all()
        
        # 计算总页数
        total_pages = (
            (total_count + page_params.size - 1) // page_params.size
            if total_count > 0 else 0
        )
        
        return cls(
            items=items,
            total=total_count,
            page=page_params.page,
            size=page_params.size,
            total_pages=total_pages
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict: 分页结果字典
        """
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "size": self.size,
            "total_pages": self.total_pages
        } 