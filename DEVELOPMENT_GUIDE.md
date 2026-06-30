# Egova AI MCP Server 开发规范

本文档参考 `Python Basic Framework` 的分层方式整理，目标是在不替换现有 MCP HTTP 运行框架的前提下，让后端职责更清晰、前端协作更稳定。

## 协作总则

- 本项目遵循根目录 `AGENTS.md` 中的全局协作规范。
- 每次完成代码、文档或资源修改后必须提交 commit，但不要 push。
- 每次修改后都要追加 `D:\worklog\YYYY-MM-DD\egova-ai-mcp-server.md` 工作日志。
- 提交前必须确认没有配置、数据库、日志、构建产物、依赖目录或大文件混入。
- 如果 `git status` 中出现不该提交的文件，优先更新 `.gitignore` 或清理暂存区。

## 后端结构

当前后端保留 `backend/app` 作为应用根目录：

- `api/`：只处理路由、请求解析、权限信息、响应封装。
- `services/`：处理业务规则、流程编排、事务提交和复杂序列化。
- `repositories/`：封装数据库查询和写入，新增模块优先在这里沉淀数据访问逻辑。
- `models/`：保留 ORM 模型、数据库初始化和迁移脚本。
- `server/`：保留 MCP server 启动与协议相关代码，HTTP 框架不要替换。
- `utils/`、`middleware/`、`core/`：保留横向能力，例如日志、鉴权、分页、配置。

推荐调用链：

```text
api route -> service -> repository -> model/database
```

## 后端约定

- API 层不要直接拼复杂 SQL，不直接提交事务。
- Service 层负责业务判断、权限相关业务规则、跨 repository 编排。
- Repository 层默认只做数据访问和 `flush()`，事务由 service 统一提交。
- 现有历史代码可以渐进迁移，新功能应直接按分层方式实现。
- MCP 服务启动链路、Starlette/FastAPI 相关依赖和现有中间件注册方式保持不变。
- 修改后至少执行 `python -m compileall backend\app backend\run.py`。
- 数据库迁移脚本必须可重复运行；旧表名、旧字段名兼容逻辑只保留在迁移脚本中。
- 新增目录使用 snake_case，服务域建议按业务命名，例如 `mcp_template`、`published_service`、`identity`。

## 前端结构

当前前端保留 `frontend/src`：

- `api/`：接口请求统一入口。
- `views/`：页面级组件，负责页面交互和组合。
- `components/`：可复用组件。
- `types/`：接口与业务类型定义。
- `store/`：Pinia 状态。
- `styles/`：全局样式变量、组件规范和工具类。

前端页面应优先使用 Element Plus 组件和项目已有样式变量，避免在页面内大量覆盖 `.el-*` 全局类。页面级样式应通过语义化 class 限定作用域。

## 前端命名

- `api/` 文件按业务资源命名，统一 kebab-case，例如 `mcp-template.ts`、`published-service.ts`、`mcp-auth.ts`。
- `views/` 下业务目录统一 kebab-case，例如 `mcp-template/`、`published-service/`、`statistics/`。
- `types/` 文件与对应业务保持一致，例如 `mcp-template.ts`。
- Vue 组件文件使用 PascalCase，例如 `AppSidebar.vue`、`ServiceParamsManager.vue`。
- 禁止新增含糊文件名，例如 `mcp.ts`、`server.ts`、`common.ts`、`utils.ts`；确实需要公共能力时，应按用途命名，如 `request.ts`、`date-format.ts`。

## 前端样式约定

- 前端样式参考 egova UrbanPro 基础平台规范，优先使用 `--common-*`、`--zartd-*`、`--header-*`、`--menu-*` CSS 变量。
- 页面和组件样式不要硬编码颜色；新增语义色先补充到 `frontend/src/styles/index.scss` 的 token 区。
- 圆角按 4px、8px、12px 分级使用；普通控件 4px/8px，页面大面板和弹窗可使用 12px，避免业务卡片大量使用 16px/20px 以上圆角。
- 管理后台以紧凑、清晰、可扫描为主，避免脱离基础平台风格的大面积自定义渐变和过重阴影。
- 应用采用左侧主导航 + 右侧内容区；页面根容器推荐使用 `.app-page`，内容面板推荐使用 `.app-panel` 或 `.app-content-panel`。
- 页面之间统一 `16px` 间距，搜索栏、表格、分页、卡片使用白底、轻边框、轻阴影。
- 页面背景采用统一浅灰蓝工作台底纹；卡片、表格、列表必须放在白色或浅色承载面板内，不允许大面积裸露空白底。
- 页面级布局优先复用 `PageContainer`、`PageHeader`、`SearchToolbar`、`StatusDot`；表格分页和确认操作优先复用 `useTable`、`useConfirmAction`。
- 卡片默认不悬浮上移；只有可点击卡片允许轻微边框/阴影变化，不使用明显 `translateY` 上浮。
- 表格头部使用浅色背景，行 hover 只做浅主色底。
- 按钮保留 Element Plus 类型语义，避免渐变按钮；Tag 使用浅底状态色，避免高饱和色块成片出现。
- 搜索、筛选、分页、空状态和加载状态需要完整。
- 文字不应依赖固定宽度挤压，列表卡片需要明确的最小高度和溢出策略。
- 禁止在业务页面中继续新增玻璃态、`backdrop-filter`、强渐变背景、大面积发光阴影、20px 以上圆角和卡片套卡片。
- `.card-content`、`.card-info` 等内部布局类不得作为全局卡片选择器使用，避免误伤不同组件。
- 不提交 `node_modules`、构建产物、锁文件、运行日志、数据库和本地配置。

## 前端页面模板

- 管理列表页：页面根容器 + 搜索工具栏 + 内容承载面板 + 表格/列表 + 分页，分页靠右并属于内容区域。
- 卡片广场页：左侧分类面板 + 右侧搜索工具栏 + 浅色列表面板 + 白色卡片列表，卡片高度、标题、描述、footer 位置保持一致。
- 详情工作台页：顶部信息面板 + 右侧操作/状态面板 + 统一 tabs 面板，tabs 内容使用白色/浅色承载区。
- 统计看板页：概览面板 + 分组指标卡片 + 趋势/排行表格，指标卡片固定高度并垂直居中。

## 新功能检查清单

- 是否保持现有 MCP HTTP 框架和启动方式。
- API 是否只负责 HTTP 相关工作。
- 业务规则是否进入 service。
- 数据查询/写入是否进入 repository。
- 前端 API 是否集中在 `frontend/src/api`。
- 页面样式是否复用全局变量和现有组件规范。
- 是否执行必要的 Python 编译、前端构建或页面验收。
- 是否按 `AGENTS.md` 要求记录 worklog 并提交 commit。

## 验证建议

按修改范围选择验证项：

- 全量快速验证：`powershell -ExecutionPolicy Bypass -File scripts/verify.ps1`
- 后端结构或服务逻辑：`conda run -n mcp python -m py_compile ...`
- 后端启动链路：`conda run -n mcp python -m py_compile run.py`
- 前端结构或样式：`cd frontend && yarn build`
- 页面级 UI：浏览器访问登录页、模板广场、服务管理、统计分析、系统管理等关键页面。
- 文档或截图：检查 Markdown 链接和图片大小，避免提交过大的文档资源。
