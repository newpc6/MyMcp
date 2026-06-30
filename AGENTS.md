# AGENTS.md

本文件用于记录当前项目的协作约定。所有自动化助手和开发者在本仓库内修改代码、文档或资源时，应优先遵守本文档。

## 基本原则

- 修改前先理解现有结构和命名，不为单个问题引入新的风格。
- 后端保持现有 MCP HTTP 运行框架，不替换框架、不绕过现有启动链路。
- 前端以基础平台风格为准，优先复用现有设计 token、Element Plus 和项目公共组件。
- 不提交本地配置、数据库、日志、构建产物、依赖目录和大文件。
- 如果发现二进制文件、配置文件或构建产物出现在 `git status` 中，应先确认是否需要更新 `.gitignore`，不要直接提交。

## 分支与提交

- 每次完成代码或文档修改后必须提交 commit。
- 不要 push，除非用户明确要求。
- 提交前检查 `git status --short`，确认暂存内容只包含本次任务需要的文件。
- 提交信息使用简洁英文，例如：
  - `docs: update development guide`
  - `refactor: standardize module naming`
  - `style: polish login page`

## 工作日志

每次修改后都需要追加工作日志：

1. 检查 `D:\worklog\` 下是否存在当天日期目录，例如 `2026-06-30`。
2. 如果不存在则创建。
3. 在日期目录下检查是否存在当前项目 Markdown 文件：`egova-ai-mcp-server.md`。
4. 如果不存在则创建。
5. 追加记录本次修改内容、验证方式和提交信息。

## 后端约定

- 新增功能按 `API -> Service -> Repository -> Model` 分层。
- API 层只处理路由、请求解析、权限依赖和响应封装。
- Service 层处理业务规则、流程编排、外部接口、文件系统和运行时操作。
- Repository 层只处理数据库访问，不写业务副作用。
- Model 层只定义 ORM 结构、关系和必要的序列化。
- 数据库表名和字段名使用 snake_case，迁移脚本必须幂等。
- 修改后端后至少执行相关 `py_compile` 或启动/import 检查。

## 前端约定

- 文件和目录统一使用 kebab-case，例如 `mcp-template.ts`、`published-service/`。
- Vue 组件名使用 PascalCase，例如 `AppSidebar.vue`。
- API 文件按业务资源命名，不使用含糊的 `mcp.ts`、`server.ts` 这类泛名。
- 路由级页面放在 `frontend/src/views/{module}/`。
- 业务组件优先放在对应页面的 `components/`，跨页面复用组件再放到 `frontend/src/components/`。
- 样式优先使用 `frontend/src/styles` 中的 token 和公共类，避免大面积硬编码颜色、阴影和渐变。
- 修改前端后执行 `yarn build`；涉及界面时用浏览器验证关键页面。

## 文档约定

- 项目文档放在 `docs/`，Markdown 文档需要进入版本管理。
- README 面向使用者，保持简洁，放安装、运行、界面预览和常用说明。
- `DEVELOPMENT_GUIDE.md` 面向开发者，记录结构、命名、验证和发布流程。
- 设计规范、开发规范和功能规划放在 `docs/` 下，避免散落在根目录。
