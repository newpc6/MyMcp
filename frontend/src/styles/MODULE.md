# 前端全局样式模块

## 职责边界

`frontend/src/styles/` 存放全局样式入口、设计 token（变量）、mixin 工具库、组件基础样式和 Element Plus 覆盖。

入口文件 `index.scss` 由 `main.ts` 全局加载，负责导入所有子模块。

## 目录/文件说明

- `index.scss`：全局样式入口，使用 `@use` 汇聚所有子模块。
- `variables.scss`：SCSS 变量定义（颜色、字体、间距、阴影、断点等）。
- `mixins.scss`：SCSS mixin 工具库（flex、text-ellipsis、scrollbar 等）。
- `card.scss`：卡片相关基础样式。
- `table.scss`：表格相关基础样式。
- `components/`：组件基础样式目录。
  - `index.scss`：汇总导入所有组件样式。
  - `form.scss`、`dialog.scss`、`pagination.scss` 等：对应组件的基础样式和 Element Plus 覆盖。

## 核心约定

### SCSS 模块系统

- 使用 `@use` / `@forward` 替代已弃用的 `@import`。
- 入口 `index.scss` 对变量和 mixin 使用 `@use '...' as *` 保持无命名空间引用。
- 组件样式文件按需显式 `@use '../variables' as *` 引入变量，不再依赖全局作用域。
- 使用 `map.get()` 替代已弃用的 `map-get()`，需同时 `@use 'sass:map'`。

### 设计 token

- 优先使用 `var(--common-*)` CSS 变量，避免硬编码颜色。
- `variables.scss` 中 $ 变量仍可被 SCSS 编译期引用，但页面/组件运行时样式应使用 CSS 变量。

## 依赖关系

```
index.scss
  → variables.scss (as *)
  → mixins.scss (as *, 内部 @use variables as *)
  → card.scss
  → table.scss
  → components/index.scss
      → pagination.scss (@use ../variables)
      → table.scss
      → action-search-card.scss
      → card.scss
      → form.scss (@use ../variables + sass:map)
      → button.scss
      → dialog.scss (@use ../variables + sass:map)
```

## 验证方式

- 修改样式后运行 `cd frontend && yarn build`，不应出现 Sass @import / global-builtin / legacy-js-api deprecation warning。

## 改动记录

- 2026-06-30：Sass `@import` 迁移到 `@use`/`@forward`；`map-get` 改为 `map.get`；新增 `@use 'sass:map'` 和 `@use '../variables'` 显式导入；同时配置 `api: 'modern-compiler'` 消除 legacy-js-api warning。