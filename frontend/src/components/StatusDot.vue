<template>
  <span class="status-dot" :class="dotClass">
    <span class="status-dot__indicator" />
    <span v-if="showText" class="status-dot__text">{{ displayText }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export type StatusDotType = 'success' | 'warning' | 'danger' | 'info' | 'default';

const STATUS_MAP: Record<StatusDotType, { label: string }> = {
  success: { label: '成功' },
  warning: { label: '警告' },
  danger: { label: '异常' },
  info: { label: '信息' },
  default: { label: '默认' }
};

const BUSINESS_STATUS_MAP: Record<string, { type: StatusDotType; label: string }> = {
  running: { type: 'success', label: '运行中' },
  active: { type: 'success', label: '启用' },
  success: { type: 'success', label: '成功' },
  enabled: { type: 'success', label: '启用' },
  stopped: { type: 'default', label: '已停止' },
  inactive: { type: 'default', label: '停用' },
  disabled: { type: 'default', label: '禁用' },
  warning: { type: 'warning', label: '警告' },
  pending: { type: 'warning', label: '待处理' },
  error: { type: 'danger', label: '异常' },
  failed: { type: 'danger', label: '失败' },
  danger: { type: 'danger', label: '异常' },
  info: { type: 'info', label: '信息' }
};

const props = withDefaults(defineProps<{
  /** 状态类型 */
  type?: StatusDotType;
  /** 业务状态值，如 running/stopped/error */
  status?: string;
  /** 自定义显示文本，传入后覆盖默认映射 */
  text?: string;
  /** 是否显示文本 */
  showText?: boolean;
}>(), {
  type: 'default',
  showText: true
});

defineOptions({
  name: 'StatusDot'
});

const normalizedStatus = computed(() => {
  if (!props.status) return undefined;
  return BUSINESS_STATUS_MAP[props.status.toLowerCase()];
});

const resolvedType = computed(() => normalizedStatus.value?.type ?? props.type);

const dotClass = computed(() => `status-dot--${resolvedType.value}`);

const displayText = computed(() => {
  if (props.text !== undefined) return props.text;
  if (normalizedStatus.value) return normalizedStatus.value.label;
  return STATUS_MAP[props.type]?.label ?? props.type;
});
</script>

<style scoped>
.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.status-dot__indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot__text {
  color: var(--common-text-color);
  font-size: var(--common-font-size-base);
  line-height: 1;
}

/* 成功: 绿色 */
.status-dot--success .status-dot__indicator {
  background-color: var(--common-success-color);
}

/* 警告: 橙色 */
.status-dot--warning .status-dot__indicator {
  background-color: var(--common-warning-color);
}

/* 异常: 红色 */
.status-dot--danger .status-dot__indicator {
  background-color: var(--common-error-color);
}

/* 信息: 蓝色 */
.status-dot--info .status-dot__indicator {
  background-color: var(--common-primary-color);
}

/* 默认: 灰色 */
.status-dot--default .status-dot__indicator {
  background-color: var(--common-text-color-lighter);
}
</style>
