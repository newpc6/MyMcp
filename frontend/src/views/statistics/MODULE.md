# 统计分析页面模块

## 职责边界

统计分析页面展示 MCP 模板、分组、发布服务和工具调用相关统计信息，包括概览卡片、趋势分析、排行榜和工具调用详情。

## 文件结构

- `index.vue`：页面入口，负责加载统计数据、分页状态和子组件编排。
- `components/StatisticsOverview.vue`：服务、模板和调用概览。
- `components/StatisticsTrend.vue`：统计趋势和汇总。
- `components/RankingDashboard.vue`：分组和模板排行榜。
- `components/ModuleRanking.vue`：模板发布排名。
- `components/ToolRanking.vue`：工具调用排名。
- `components/ServiceRanking.vue`：服务调用排名。
- `components/ToolExecutionDetails.vue`：工具调用明细。

## 样式约束

- 页面背景使用全局默认灰色，不在页面内强行设为纯白。
- 主内容和卡片使用白色背景、1px 边框、4-8px 为主的圆角和轻阴影。
- 避免大面积渐变、玻璃态、强悬浮位移和过重阴影。
- 标题、图标、数值和说明文字需要保持垂直居中和统一行高。
- 优先使用 `var(--common-*)` 设计 token，不新增局部色板。

## 依赖关系

- API：`frontend/src/api/statistics.ts`
- 工具：`frontend/src/utils/table`
- 组件库：Element Plus、`@element-plus/icons-vue`

## 验证方式

- 修改后运行 `cd frontend && yarn build`。
- 浏览器访问 `/statistics`，检查概览卡片、趋势卡片、排行榜、详情表格的对齐、留白、边框和颜色一致性。

## 改动记录

- 2026-06-30：统一统计页卡片、排行榜、趋势和详情样式，去除重渐变、玻璃态和悬浮位移，改为白底卡片、边框和轻阴影。
