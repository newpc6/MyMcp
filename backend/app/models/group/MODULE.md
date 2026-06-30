# MCP 分组模型模块

## 职责边界

`backend/app/models/group/` 定义 MCP 模板分组 ORM 模型。模型层只描述表结构和简单序列化，不直接打开数据库连接或执行统计 SQL。

## 模型

- `McpGroup`
  - 表名：`mcp_template_groups`
  - 主要字段：`id`、`name`、`description`、`icon`、`order`、`user_id`、`created_at`、`updated_at`
  - `to_dict(templates_count=None, include_modules_count=True)` 接收外部传入的模板数量，兼容旧调用参数。

## 上下游依赖

- 上游 Service：`backend/app/services/group/service.py`
- 数据访问：`backend/app/repositories/mcp_template_group_repository.py`
- 下游关联：`mcp_templates.category_id`

## 风险点

- 分组删除会解除模板关联，具体事务由 `GroupService` 控制。
- 历史字段仍使用 `category_id` 表示模板所属分组，后续如重命名需要配合迁移和前后端契约。

## 验证方式

```powershell
cd backend
python -m py_compile app/models/group/group.py
```

## 改动记录

- 2026-06-30：移除模型层统计 SQL，改由 `McpTemplateGroupRepository` 查询；`to_dict` 保留旧参数兼容。
