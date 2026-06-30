# 前端公共组件模块

## 职责边界

`frontend/src/components/` 存放跨页面复用的 UI 组件。业务强相关组件应优先放在对应页面目录的 `components/` 下，只有多个页面复用或承载平台级规范时才进入本目录。

## 当前公共组件

- `AppSidebar.vue`：应用左侧菜单和收起展开交互。
- `ActionSearchCard.vue`：带操作区的搜索卡片。
- `PageContainer.vue`：白色主内容容器，提供标题、内容和页脚插槽。
- `PageHeader.vue`：紧凑页面标题区，支持图标、说明和操作区。
- `SearchToolbar.vue`：统一搜索/筛选工具栏，支持左侧、主体和操作区插槽。
- `StatusDot.vue`：状态圆点，支持 `type` 和 `status` 映射，可只显示圆点或附带文本。
- `index.ts`：公共组件导出入口。

## 设计约束

- Vue 组件使用 PascalCase 文件名。
- 样式优先使用 `var(--common-*)` 和 Element Plus token，不在组件中新增业务色板。
- 公共组件不得直接调用业务 API、路由或 store。
- 页面背景不由公共容器强行设置，页面默认灰色背景由全局布局控制，主内容区域使用白色容器。

## 验证方式

- 修改公共组件后运行 `cd frontend && yarn build`。
- 涉及视觉变化时使用浏览器检查至少一个使用该组件的页面。

## 改动记录

- 2026-06-30：新增 `PageContainer`、`PageHeader`、`SearchToolbar`、`StatusDot` 和公共导出入口，用于沉淀平台统一页面结构和状态展示。
