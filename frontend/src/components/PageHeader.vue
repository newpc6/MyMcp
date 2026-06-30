<template>
  <div class="page-header">
    <div class="page-header__left">
      <div v-if="$slots.icon" class="page-header__icon">
        <slot name="icon" />
      </div>
      <div class="page-header__text">
        <h1 v-if="title" class="page-header__title">{{ title }}</h1>
        <p v-if="subtitle || $slots.subtitle" class="page-header__subtitle">
          <slot name="subtitle">{{ subtitle }}</slot>
        </p>
      </div>
    </div>
    <div v-if="$slots.actions || $slots.default" class="page-header__actions">
      <slot name="actions" />
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'PageHeader'
});

defineProps<{
  title?: string;
  subtitle?: string;
}>();
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 56px;
  padding: 12px 20px;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-lg);
  box-shadow: var(--common-shadow-xs);
  gap: 16px;
}

.page-header__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex: 1;
}

.page-header__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  color: var(--common-primary-color);
  background: var(--common-primary-background-color);
  border-radius: var(--common-radius-md);
  font-size: 18px;
}

.page-header__text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  gap: 2px;
}

.page-header__title {
  margin: 0;
  color: var(--common-text-color-heavy);
  font-size: var(--common-font-size-title-md);
  font-weight: 600;
  line-height: 28px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-header__subtitle {
  margin: 0;
  color: var(--common-text-color-light);
  font-size: var(--common-font-size-secondary);
  line-height: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
</style>
