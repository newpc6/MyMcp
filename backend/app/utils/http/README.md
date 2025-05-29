# HTTP工具包使用说明

## 分页功能使用指南

HTTP工具包提供了通用的分页功能实现，可以大大简化API中分页功能的开发。

### 直接在API路由中使用

```python
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.utils.http import PageParams, PageResult, paginate_dependency
from app.db.database import get_db
from app.models.item import Item

router = APIRouter()

@router.get("/items")
async def list_items(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(paginate_dependency())
):
    # 创建查询
    query = db.query(Item)
    
    # 应用分页并返回结果
    result = PageResult.from_query(query, page_params)
    
    # 转换为字典并返回
    return result.to_dict()
```

### 在请求处理函数中手动解析分页参数

```python
from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from app.utils.http import get_page_params, PageResult
from app.db.database import get_db
from app.models.item import Item

router = APIRouter()

@router.get("/items")
async def list_items(request: Request, db: Session = Depends(get_db)):
    # 获取分页参数
    page_params = get_page_params(request, default_limit=20, max_limit=100)
    
    # 创建查询
    query = db.query(Item)
    
    # 应用分页并返回结果
    result = PageResult.from_query(query, page_params)
    
    # 转换为字典并返回
    return result.to_dict()
```

### 在服务层使用

```python
from sqlalchemy.orm import Session
from app.utils.http import PageParams, PageResult
from app.models.item import Item

class ItemService:
    def __init__(self, db: Session):
        self.db = db
    
    def list_items(self, page_params: PageParams):
        # 创建查询
        query = self.db.query(Item)
        
        # 应用分页并返回结果
        return PageResult.from_query(query, page_params)
```

然后在API中:

```python
@router.get("/items")
async def list_items(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(paginate_dependency())
):
    service = ItemService(db)
    result = service.list_items(page_params)
    return result.to_dict()
```

## 自定义分页参数

可以自定义默认每页条数和最大每页条数:

```python
# 创建自定义分页依赖，默认每页50条，最大100条
custom_pagination = paginate_dependency(default_limit=50, max_limit=100)

@router.get("/items")
async def list_items(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(custom_pagination)
):
    # 使用page_params
    pass
```

## 分页结果构建

### 基本分页响应构建

使用 `build_page_response` 构建标准的分页响应：

```python
from app.utils.http import build_page_response, PageParams

# 示例数据
items = [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]
total = 100
page_params = PageParams(page=1, size=10, offset=0)

# 构建分页响应
response = build_page_response(items, total, page_params)
# 返回:
# {
#     "items": [...],
#     "total": 100,
#     "page": 1,
#     "size": 10,
#     "total_pages": 10
# }
```

## 实际使用示例

### 在服务层中使用

```python
from app.utils.http import build_page_response, PageParams

class MarketplaceService:
    async def list_items(self, page_params: PageParams):
        # 查询数据
        items, total = await self.query_items(page_params)
        
        # 构建响应
        return build_page_response(items, total, page_params)
```

### 在API路由中使用

```python
from fastapi import Depends
from app.utils.http import paginate_dependency, PageParams, build_page_response

@router.get("/marketplace/items")
async def list_marketplace_items(
    page_params: PageParams = Depends(paginate_dependency())
):
    # 查询逻辑
    items = query_marketplace_items(page_params)
    total = count_marketplace_items()
    
    # 返回统一格式的分页响应
    return build_page_response(items, total, page_params)
```

## 迁移现有代码

如果你的代码当前是手动构建分页响应，可以替换为使用这些工具方法：

### 替换前
```python
# 旧的手动构建方式
return {
    "items": result_items,
    "total": total_count,
    "page": page_params.page,
    "size": page_params.size,
    "total_pages": total_pages
}
```

### 替换后
```python
# 使用工具方法
from app.utils.http import build_page_response

return build_page_response(result_items, total_count, page_params)
```

这样可以确保分页响应格式的一致性，并简化代码维护。 