# 后端 Repository 模块

## 职责边界

`backend/app/repositories/` 是数据访问层，只负责数据库查询和持久化，不处理 HTTP、权限、响应封装、外部服务或运行时副作用。

## 当前 Repository

- `user_repository.py`：用户数据访问。
- `tenant_repository.py`：租户数据访问。
- `mcp_template_group_repository.py`：MCP 模板分组计数、统计和分组排行榜查询。
- `mcp_template_repository.py`：MCP 模板统计、排行榜查询。

## 设计约束

- Repository 方法接收 SQLAlchemy `Session`，不在内部自行打开 `get_db()`。
- Service 层负责事务生命周期、业务校验、权限和响应结构。
- SQL 字段名和表名使用 snake_case。
- 复杂 SQL 迁移到 Repository 后，Model 层只保留 ORM 字段和必要序列化。

## 验证方式

- 修改后执行相关 Python 语法检查，例如：

```powershell
cd backend
python -m py_compile app/repositories/mcp_template_repository.py
python -m py_compile app/repositories/mcp_template_group_repository.py
```

- 如涉及 Service 调用链，补充 import 检查或接口冒烟测试。

## 改动记录

- 2026-06-30：新增 `McpTemplateGroupRepository`，承接分组模板计数、分组统计和分组排行榜查询。
- 2026-06-30：新增 `McpTemplateRepository`，承接模板统计（to_stat_dict）和模板排行榜 SQL，从 `McpModule` 模型迁移。
