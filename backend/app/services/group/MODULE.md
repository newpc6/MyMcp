# MCP 分组服务模块

## 职责边界

`backend/app/services/group/` 负责 MCP 模板分组的业务编排，包括分组列表、详情、创建、更新、删除、分页统计和模板分组绑定。

## 公开入口

- `group_service.list_group`
- `group_service.stat_group`
- `group_service.get_category`
- `group_service.create_category`
- `group_service.update_category`
- `group_service.delete_category`
- `group_service.update_module_category`

## 依赖关系

- Model：`McpGroup`、`McpModule`
- Repository：`McpTemplateGroupRepository`
- 工具：`add_edit_permission`、`PageParams`、`build_page_response`

## 设计约束

- Service 层负责打开 `get_db()` 和控制提交/回滚。
- 复杂统计查询通过 Repository 完成。
- 公开方法名和返回结构兼容既有 API，不在本模块直接修改路由契约。

## 验证方式

```powershell
cd backend
python -m py_compile app/services/group/service.py
python -c "from app.services.group.service import group_service; print(type(group_service).__name__)"
```

## 改动记录

- 2026-06-30：分组计数和排行榜统计改为调用 `McpTemplateGroupRepository`，Service 保持原有公开方法和响应结构。
