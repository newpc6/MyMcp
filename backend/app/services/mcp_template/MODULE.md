# MCP 模板服务模块

## 职责边界

`backend/app/services/mcp_template/` 负责 MCP 模板的业务编排，包括模板分页、列表、详情、工具函数、复制、扫描仓库模板和统计排行榜。

## 公开入口

- `mcp_template_service.page_modules`
- `mcp_template_service.list_modules`
- `mcp_template_service.get_module`
- `mcp_template_service.get_module_tools`
- `mcp_template_service.get_tool`
- `mcp_template_service.scan_repository_modules`
- `mcp_template_service.create_module`
- `mcp_template_service.update_module`
- `mcp_template_service.delete_module`
- `mcp_template_service.clone_module`
- `mcp_template_service.get_module_stats_ranking`

## 依赖关系

- Model：`McpModule`、`McpTool`、`McpGroup`、`ToolExecution`
- Repository：`McpTemplateRepository`
- Service：`published_service.service_manager`
- 工具：`add_edit_permission`、`PageParams`、`build_page_response`

## 设计约束

- Service 层保持既有 API 返回结构，不在本模块改变路由契约。
- 模板统计排行榜通过 `McpTemplateRepository` 查询。
- 模板代码、Markdown 和配置 schema 的读写需要保持向后兼容。
- 不更换 MCP HTTP 运行框架，不绕过已有发布服务链路。

## 验证方式

```powershell
cd backend
python -m py_compile app/services/mcp_template/service.py
python -c "from app.services.mcp_template.service import mcp_template_service; print(type(mcp_template_service).__name__)"
```

## 改动记录

- 2026-06-30：`get_module_stats_ranking` 改为通过 `McpTemplateRepository` 查询，公开方法签名和返回结构保持不变。
