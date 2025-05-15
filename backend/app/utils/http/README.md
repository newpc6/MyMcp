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