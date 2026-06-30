# HTTP 工具模块 (utils/http)

## 职责边界

提供后端 HTTP 层常用的轻量工具，包括分页参数解析、分页结果封装和通用请求/响应辅助。该模块不访问数据库连接，不承载业务规则。

## 目录/文件说明

- `pagination.py`：`PageParams` 分页参数模型和 `PageResult[T]` 分页结果模型。
- `utils.py`：HTTP 相关辅助函数。
- `README.md`：历史说明文档。

## 公开接口

- `PageParams.from_request_body(body, default_size=10, max_size=50)`：从请求体读取分页参数。
- `PageParams.from_request(request, default_size=10, max_size=50)`：从查询参数读取分页参数。
- `PageParams.from_params(page, size)`：用于 FastAPI 参数声明。
- `PageResult.from_query(query, page_params, items=None)`：从 SQLAlchemy 查询生成分页结果。
- `PageResult.to_dict()`：序列化分页结果。

## 维护约定

- Pydantic 泛型模型继承顺序使用 `BaseModel, Generic[T]`，避免泛型模型 warning。
- 分页工具只负责参数和结果封装，具体过滤条件、排序和权限逻辑放在 Repository/Service。

## 验证方式

```powershell
cd backend
conda run -n mcp python -m py_compile app/utils/http/pagination.py
conda run -n mcp python -c "from app.utils.http.pagination import PageParams, PageResult; print(PageParams.__name__, PageResult.__name__)"
```

## 改动记录

- 2026-06-30：修复 `PageResult` Pydantic 泛型继承顺序 warning。
