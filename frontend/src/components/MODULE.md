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
- `DataTable.vue`：基于 Element Plus `el-table` + `el-pagination` 的通用数据表格组件，封装 loading、空态、分页和操作插槽，不绑定具体业务。
- `index.ts`：公共组件导出入口。

## DataTable 使用说明

### Props

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `data` | `unknown[]` | `[]` | 表格数据 |
| `loading` | `boolean` | `false` | 加载状态 |
| `total` | `number` | `0` | 总条目数 |
| `page` | `number` | `1` | 当前页码（支持 `v-model:page`） |
| `pageSize` | `number` | `10` | 每页条数（支持 `v-model:pageSize`） |
| `pageSizes` | `number[]` | `[10,20,50,100]` | 每页条数选项 |
| `rowKey` | `string` | `'id'` | 行标识字段 |
| `showPagination` | `boolean` | `true` | 是否显示分页 |
| `emptyText` | `string` | `'暂无数据'` | 空数据提示文案 |
| `compact` | `boolean` | `false` | 紧凑模式（减小内边距） |
| `paginationLayout` | `string` | `'total, sizes, prev, pager, next, jumper'` | 分页组件布局 |
| `paginationBackground` | `boolean` | `true` | 分页按钮是否带背景色 |

### Emits

| 事件 | 参数 | 说明 |
|---|---|---|
| `update:page` | `number` | 页码变化（v-model 双向绑定） |
| `update:pageSize` | `number` | 每页条数变化（v-model 双向绑定） |
| `page-change` | `number` | 页码变化（与 update:page 同步触发） |
| `size-change` | `number` | 每页条数变化（与 update:pageSize 同步触发） |
| `refresh` | - | 刷新事件（通过工具栏 slot 手动触发） |
| `sort-change` | `any` | 排序变化（透传 el-table sort-change） |
| `selection-change` | `any` | 选择变化（透传 el-table selection-change） |

### Slots

| 插槽 | 说明 |
|---|---|
| `default` | 列定义（直接放入 `el-table-column`） |
| `toolbar` | 表格上方工具栏 |
| `empty` | 自定义空数据展示 |
| `pagination-extra` | 分页左侧额外内容 |

### 使用示例

```vue
<DataTable
  v-model:page="page"
  v-model:pageSize="size"
  :data="tableData"
  :total="total"
  :loading="loading"
  row-key="id"
>
  <template #toolbar>
    <el-button type="primary" @click="fetchData">查询</el-button>
  </template>
  <el-table-column type="index" label="#" width="60" />
  <el-table-column prop="name" label="名称" />
  <el-table-column label="操作" width="120">
    <template #default="{ row }">
      <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
    </template>
  </el-table-column>
</DataTable>
```

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
- 2026-06-30：新增 `DataTable` 通用数据表格组件，基于 Element Plus `el-table` + `el-pagination`，封装 loading、空态、分页和操作插槽。
