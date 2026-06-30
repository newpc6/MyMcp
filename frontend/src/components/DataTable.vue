<template>
  <div
    class="data-table"
    :class="{
      'data-table--compact': compact,
      'data-table--loading': loading && data.length === 0
    }"
  >
    <!-- 工具栏插槽 -->
    <div v-if="$slots.toolbar" class="data-table__toolbar">
      <slot name="toolbar" />
    </div>

    <!-- 表格区域 -->
    <div class="data-table__body">
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="data"
        :row-key="resolvedRowKey"
        :element-loading-text="loadingText"
        :element-loading-background="loadingBg"
        v-bind="$attrs"
        @sort-change="$emit('sort-change', $event)"
        @selection-change="$emit('selection-change', $event)"
      >
        <slot />
        <template #empty>
          <slot name="empty">
            <div class="data-table__empty">
              <el-empty :description="emptyText" :image-size="80" />
            </div>
          </slot>
        </template>
      </el-table>
    </div>

    <!-- 分页区域 -->
    <div v-if="showPagination" class="data-table__pagination">
      <div class="data-table__pagination-extra">
        <slot name="pagination-extra" />
      </div>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="currentPageSize"
        :total="total"
        :page-sizes="pageSizes"
        :layout="paginationLayout"
        :background="paginationBackground"
        :small="compact"
        :disabled="loading"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

defineOptions({
  name: 'DataTable'
});

const props = withDefaults(defineProps<{
  /** 表格数据 */
  data: unknown[];
  /** 加载状态 */
  loading?: boolean;
  /** 总条目数 */
  total?: number;
  /** 当前页码 */
  page?: number;
  /** 每页条数 */
  pageSize?: number;
  /** 每页条数选项 */
  pageSizes?: number[];
  /** 行标识字段 */
  rowKey?: string;
  /** 是否显示分页 */
  showPagination?: boolean;
  /** 空数据提示文案 */
  emptyText?: string;
  /** 紧凑模式 */
  compact?: boolean;
  /** 分页布局 */
  paginationLayout?: string;
  /** 分页是否带背景 */
  paginationBackground?: boolean;
  /** 加载提示文案 */
  loadingText?: string;
  /** 加载遮罩背景色 */
  loadingBg?: string;
}>(), {
  data: () => [],
  loading: false,
  total: 0,
  page: 1,
  pageSize: 10,
  pageSizes: () => [10, 20, 50, 100],
  rowKey: 'id',
  showPagination: true,
  emptyText: '暂无数据',
  compact: false,
  paginationLayout: 'total, sizes, prev, pager, next, jumper',
  paginationBackground: true,
  loadingText: '加载中...',
  loadingBg: 'var(--common-panel-background-color)'
});

const emit = defineEmits<{
  (e: 'update:page', val: number): void;
  (e: 'update:pageSize', val: number): void;
  (e: 'page-change', val: number): void;
  (e: 'size-change', val: number): void;
  (e: 'refresh'): void;
  (e: 'sort-change', val: any): void;
  (e: 'selection-change', val: any): void;
}>();

const tableRef = ref();

const currentPage = computed({
  get: () => props.page,
  set: (val: number) => {
    emit('update:page', val);
    emit('page-change', val);
  }
});

const currentPageSize = computed({
  get: () => props.pageSize,
  set: (val: number) => {
    emit('update:pageSize', val);
    emit('size-change', val);
  }
});

const resolvedRowKey = computed(() => {
  if (props.rowKey) return props.rowKey;
  return undefined;
});
</script>

<style scoped>
.data-table {
  display: flex;
  flex-direction: column;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-lg);
  box-shadow: var(--common-shadow-xs);
  overflow: hidden;
}

.data-table__toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid var(--common-border-color);
  background: var(--common-surface-muted-color);
}

.data-table__body {
  flex: 1;
  min-height: 0;
}

.data-table__pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--common-border-color);
  background: var(--common-surface-muted-color);
}

.data-table__pagination-extra {
  display: flex;
  align-items: center;
  gap: 8px;
}

.data-table__empty {
  padding: 32px 0;
}

/* 紧凑模式 */
.data-table--compact .data-table__toolbar {
  padding: 8px 12px;
}

.data-table--compact .data-table__pagination {
  padding: 8px 12px;
}

/* 表格内部样式重置 */
.data-table :deep(.el-table) {
  --el-table-border-color: var(--common-border-color);
  --el-table-header-bg-color: var(--common-table-header-background-color);
  --el-table-row-hover-bg-color: var(--common-hover-background-color);
  --el-table-text-color: var(--common-text-color);
  --el-table-header-text-color: var(--common-text-color-heavy);
}

.data-table :deep(.el-table th.el-table__cell) {
  background-color: var(--common-table-header-background-color);
  border-bottom: 1px solid var(--common-border-color);
  font-weight: 600;
  font-size: var(--common-font-size-base);
}

.data-table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background-color: var(--common-hover-background-color);
}

.data-table :deep(.el-loading-mask) {
  background-color: var(--common-panel-background-color);
}

/* 分页样式统一 */
.data-table :deep(.el-pagination) {
  justify-content: flex-end;
}

.data-table :deep(.el-pagination .el-select .el-input) {
  width: 110px;
}
</style>
