# 前端组合函数模块

## 职责边界

`frontend/src/composables/` 存放跨页面复用的 Vue 组合式函数。组合函数应保持业务无关，业务 API、具体字段映射和页面副作用由调用方注入。

## 当前组合函数

- `useTable.ts`：管理分页、查询条件、加载状态、重置和刷新逻辑，通过 `fetchFn` 注入数据请求。
- `useConfirmAction.ts`：封装确认弹窗、执行中状态和重复提交保护，不吞掉真实异常。

## 使用约束

- 组合函数文件名使用 camelCase。
- 不直接依赖具体页面、路由或业务 API。
- 错误处理默认交给调用方，除明确取消/关闭外不吞异常。
- 分页结果建议使用 `frontend/src/types/page.ts` 中的 `PageResult<T>` 和 `TableState<T>`。

## 验证方式

- 修改后运行 `cd frontend && yarn build`。
- 被页面接入后需要验证加载、搜索、重置、翻页和页大小切换。

## 改动记录

- 2026-06-30：新增 `useTable` 和 `useConfirmAction`，用于后续收敛页面重复分页和确认操作逻辑。
