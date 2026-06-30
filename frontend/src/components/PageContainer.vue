<template>
  <div class="page-container" :class="{ 'is-compact': compact }">
    <div v-if="$slots.title || $slots['title-extra']" class="page-container__header">
      <div class="page-container__title-area">
        <slot name="title" />
      </div>
      <div v-if="$slots['title-extra']" class="page-container__title-extra">
        <slot name="title-extra" />
      </div>
    </div>
    <div class="page-container__body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="page-container__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'PageContainer'
});

withDefaults(defineProps<{
  compact?: boolean;
}>(), {
  compact: false
});
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-lg);
  box-shadow: var(--common-shadow-xs);
  overflow: hidden;
}

.page-container__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 56px;
  padding: 0 20px;
  border-bottom: 1px solid var(--common-border-color);
  gap: 16px;
}

.page-container__title-area {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.page-container__title-extra {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.page-container__body {
  flex: 1;
  padding: 16px 20px;
}

.page-container.is-compact .page-container__body {
  padding: 12px 16px;
}

.page-container.is-compact .page-container__header {
  min-height: 48px;
  padding: 0 16px;
}

.page-container__footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-height: 52px;
  padding: 0 20px;
  border-top: 1px solid var(--common-border-color);
  gap: 8px;
  background: var(--common-surface-muted-color);
}
</style>
