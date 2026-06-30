<template>
  <div class="search-toolbar">
    <div class="search-toolbar__left">
      <slot name="left" />
    </div>
    <div class="search-toolbar__center">
      <slot />
    </div>
    <div class="search-toolbar__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'SearchToolbar'
});
</script>

<style scoped>
.search-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-lg);
  box-shadow: var(--common-shadow-xs);
  gap: 12px;
}

.search-toolbar__left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  flex-shrink: 0;
}

.search-toolbar__center {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
  gap: 8px;
}

.search-toolbar__actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  flex-shrink: 0;
  margin-left: auto;
}

/* 内置表单行间距统一 */
.search-toolbar :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

.search-toolbar :deep(.el-form--inline .el-form-item) {
  margin-right: 12px;
}

.search-toolbar :deep(.el-input),
.search-toolbar :deep(.el-select) {
  --el-input-width: auto;
}
</style>
