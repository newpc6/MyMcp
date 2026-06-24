# Egova AI MCP Server 开发规范

本文档参考 `Python Basic Framework` 的分层方式整理，目标是在不替换现有 MCP HTTP 运行框架的前提下，让后端职责更清晰、前端协作更稳定。

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

## 前端结构

当前前端保留 `frontend/src`：

- `api/`：接口请求统一入口。
- `views/`：页面级组件，负责页面交互和组合。
- `components/`：可复用组件。
- `types/`：接口与业务类型定义。
- `store/`：Pinia 状态。
- `styles/`：全局样式变量、组件规范和工具类。

前端页面应优先使用 Element Plus 组件和项目已有样式变量，避免在页面内大量覆盖 `.el-*` 全局类。页面级样式应通过语义化 class 限定作用域。

## 前端样式约定

- 前端样式参考 egova UrbanPro 基础平台规范，优先使用 `--common-*`、`--zartd-*`、`--header-*`、`--menu-*` CSS 变量。
- 页面和组件样式不要硬编码颜色；新增语义色先补充到 `frontend/src/styles/index.scss` 的 token 区。
- 圆角按 4px、8px、16px 分级使用；普通控件 4px/8px，面板和弹窗可使用 16px。
- 管理后台以紧凑、清晰、可扫描为主，避免脱离基础平台风格的大面积自定义渐变和过重阴影。
- 搜索、筛选、分页、空状态和加载状态需要完整。
- 文字不应依赖固定宽度挤压，列表卡片需要明确的最小高度和溢出策略。
- 不提交 `node_modules`、构建产物、锁文件、运行日志、数据库和本地配置。

## 新功能检查清单

- 是否保持现有 MCP HTTP 框架和启动方式。
- API 是否只负责 HTTP 相关工作。
- 业务规则是否进入 service。
- 数据查询/写入是否进入 repository。
- 前端 API 是否集中在 `frontend/src/api`。
- 页面样式是否复用全局变量和现有组件规范。
- 是否执行必要的 Python 编译、前端构建或页面验收。
- 是否按 `AGENTS.md` 要求记录 worklog 并提交 commit。
