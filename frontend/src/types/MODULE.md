# 前端类型模块

## 职责边界

`frontend/src/types/` 存放跨页面复用的 TypeScript 类型定义。业务专属类型应按业务资源命名，通用分页、表格和搜索类型可放在 `page.ts`。

## 当前类型

- `page.ts`
  - `PageParams`：分页参数。
  - `Page`：旧分页请求结构。
  - `PageResult<T>`：统一分页返回结构。
  - `TableState<T>`：表格状态结构。
  - `SearchParams`：搜索和分页查询参数。

## 使用约束

- 新增类型优先使用明确泛型，不扩大 `any` 的使用范围。
- 与 API response 相关的类型应保持字段名与后端返回一致。
- 页面接入 `useTable` 时优先使用 `PageResult<T>` 和 `TableState<T>`。

## 验证方式

```powershell
cd frontend
yarn build
```

## 改动记录

- 2026-06-30：新增分页结果、表格状态和搜索参数类型，为 `useTable` 提供基础类型。
