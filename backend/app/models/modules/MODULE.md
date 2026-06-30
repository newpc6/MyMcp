# MCP 模板模型模块

## 职责边界

`backend/app/models/modules/` 定义 MCP 模板、模板工具、发布服务和用户等 ORM 模型。模型层只描述表结构、关系和必要序列化，不直接打开数据库连接执行统计查询。

## 当前核心模型

- `mcp_template.py`：`McpModule`，表名 `mcp_templates`，表示 MCP 模板。
- `mcp_template_tool.py`：模板工具函数模型。
- `published_service.py`：已发布 MCP 服务模型。
- `users.py`：用户模型。

## MCP 模板模型约束

- `McpModule.to_dict()` 只做字段序列化和 JSON 解析。
- 模板统计和排行榜查询由 `backend/app/repositories/mcp_template_repository.py` 承担。
- 不在模型层调用 `get_db()`，避免模型产生连接生命周期副作用。

## 验证方式

```powershell
cd backend
python -m py_compile app/models/modules/mcp_template.py
```

## 改动记录

- 2026-06-30：移除 `McpModule` 中的统计 SQL 和 `get_db()` 调用，模板统计/排行榜迁移到 `McpTemplateRepository`。
