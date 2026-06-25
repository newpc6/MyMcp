<template>
  <el-card class="module-info-card" shadow="never">
    <div class="flex items-start">
      <div class="flex-1">
        <div class="flex justify-between">
          <div class="flex">
            <el-avatar :icon="getModuleIcon(moduleInfo)" :size="32" class="mr-6"></el-avatar>
            <h2 class="text-xl font-bold mb-2">{{ moduleInfo.name }}</h2>
          </div>
          <div>
            <el-button type="primary" @click="$emit('edit')" class="mr-2" v-if="hasEditPermission">编辑</el-button>
            <el-button type="danger" @click="$emit('delete')" class="mr-2" v-if="hasEditPermission">删除</el-button>
            <el-button @click="$emit('back')" class="return-btn">返回广场</el-button>
          </div>
        </div>

        <el-descriptions :column="2" border size="small" class="module-info-descriptions">
          <el-descriptions-item label="描述" :span="2" label-class-name="info-label" content-class-name="info-content">
            {{ moduleInfo.description }}
          </el-descriptions-item>

          <el-descriptions-item label="标签" :span="2" label-class-name="info-label" content-class-name="info-content">
            <div class="flex flex-wrap">
              <el-tag v-for="tag in tags" :key="tag" size="small" class="mr-1 tag-item">{{ tag }}</el-tag>
              <el-tag size="small" :type="moduleInfo.is_hosted ? 'success' : 'primary'" class="tag-item">
                {{ moduleInfo.is_hosted ? '托管' : '本地' }}
              </el-tag>
              <el-tag size="small" type="info" class="tag-item">
                {{ moduleInfo.tools_count }} 个工具
              </el-tag>
            </div>
          </el-descriptions-item>

          <el-descriptions-item v-if="moduleInfo.author" label="作者" label-class-name="info-label"
            content-class-name="info-content">
            {{ moduleInfo.author }}
          </el-descriptions-item>
          <el-descriptions-item v-if="moduleInfo.version" label="版本" label-class-name="info-label"
            content-class-name="info-content">
            {{ moduleInfo.version }}
          </el-descriptions-item>
          <el-descriptions-item v-if="moduleInfo.creator_name" label="创建者" label-class-name="info-label"
            content-class-name="info-content">
            {{ moduleInfo.creator_name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态" label-class-name="info-label" content-class-name="info-content">
            <el-tag size="small" :type="moduleInfo.is_public ? 'success' : 'danger'">
              {{ moduleInfo.is_public ? '公开' : '私有' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" label-class-name="info-label" content-class-name="info-content">
            {{ moduleInfo.created_at }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" label-class-name="info-label" content-class-name="info-content">
            {{ moduleInfo.updated_at }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { McpModuleInfo } from '../../../types/mcp-template';

const props = defineProps<{
  moduleInfo: McpModuleInfo;
  hasEditPermission: boolean;
}>();

const emit = defineEmits<{
  (e: 'edit'): void;
  (e: 'delete'): void;
  (e: 'back'): void;
}>();

// 将标签处理为数组
const tags = computed(() => {
  if (!props.moduleInfo.tags) return [];
  if (typeof props.moduleInfo.tags === 'string') {
    return props.moduleInfo.tags.split(',').filter((t: string) => t.trim());
  }
  return props.moduleInfo.tags;
});

// 根据模块类型获取图标
function getModuleIcon(module: McpModuleInfo) {
  // 根据模块类型或名称返回不同的图标
  if (!module?.name) return 'Tools';

  if (module.name.toLowerCase().includes('tavily')) {
    return 'Search';
  } else if (module.name.toLowerCase().includes('fetch')) {
    return 'Link';
  } else if (module.name.toLowerCase().includes('github')) {
    return 'Platform';
  } else {
    return 'Tools';
  }
}
</script>

<script lang="ts">
export default {
  name: 'ModuleInfoCard'
}
</script>

<style scoped>
.module-info-card {
  border-radius: var(--common-radius-lg);
  box-shadow: var(--common-shadow-xs) !important;
  border: 1px solid var(--common-border-color);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  overflow: hidden;
  background: var(--common-panel-background-color);
  position: relative;
}

.module-info-card::before {
  display: none;
}

/* .module-info-card:hover {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12) !important;
  transform: translateY(-6px);
} */

.module-info-descriptions {
  margin-top: 16px;
  border-radius: var(--common-radius-md);
  overflow: hidden;
  border: 1px solid var(--common-border-color);
}

:deep(.el-descriptions__header) {
  background: var(--common-table-header-background-color);
  padding: 16px 20px;
  border-bottom: 1px solid var(--common-border-color);
}

:deep(.el-descriptions__body) {
  background: var(--common-panel-background-color);
}

:deep(.info-label) {
  background: var(--common-table-header-background-color) !important;
  color: var(--common-text-color) !important;
  font-weight: 600 !important;
  border-right: 1px solid var(--common-border-color) !important;
  padding: 12px 16px !important;
}

:deep(.info-content) {
  color: var(--common-text-color) !important;
  padding: 12px 16px !important;
  background: var(--common-panel-background-color) !important;
}

:deep(.el-descriptions__cell) {
  border-bottom: 1px solid var(--common-border-color) !important;
}

.return-btn {
  border-radius: var(--common-radius-md);
  transition: border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease;
  padding: 10px 20px;
  font-weight: 500;
  border: 1px solid var(--common-border-color);
  background: var(--common-panel-background-color);
  color: var(--common-text-color);
}

.return-btn:hover {
  background: var(--common-hover-background-color);
  border-color: var(--common-primary-color);
  color: var(--common-primary-color);
  transform: none;
  box-shadow: none;
}

:deep(.el-button--primary) {
  background: var(--common-primary-color);
  border: 1px solid var(--common-primary-color);
  border-radius: var(--common-radius-md);
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-button--primary:hover) {
  background: var(--zartd-primary-7);
  transform: none;
  box-shadow: none;
}

:deep(.el-button--danger) {
  background: var(--common-error-color);
  border: 1px solid var(--common-error-color);
  border-radius: var(--common-radius-md);
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-button--danger:hover) {
  background: var(--common-error-color);
  transform: none;
  box-shadow: none;
}

.tag-item {
  border-radius: var(--common-radius-sm);
  padding: 0 12px;
  height: 26px;
  line-height: 24px;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: none;
  font-weight: 500;
  border: 1px solid transparent;
}

.tag-item:hover {
  transform: none;
  box-shadow: none;
}

:deep(.el-tag--success) {
  background: var(--common-success-background-color);
  border-color: var(--common-success-color);
  color: var(--common-success-color);
}

:deep(.el-tag--primary) {
  background: var(--common-primary-background-color);
  border-color: var(--common-primary-color);
  color: var(--common-primary-color);
}

:deep(.el-tag--info) {
  background: var(--common-info-background-color);
  border-color: var(--common-border-color);
  color: var(--common-text-color-light);
}

:deep(.el-tag--danger) {
  background: var(--common-error-background-color);
  border-color: var(--common-error-color);
  color: var(--common-error-color);
}

:deep(.el-tag--warning) {
  background: var(--common-warning-background-color);
  border-color: var(--common-warning-color);
  color: var(--common-warning-color);
}

:deep(.el-avatar) {
  background: var(--common-primary-background-color);
  color: var(--common-primary-color);
  border: 1px solid var(--zartd-primary-2);
  transition: none;
}

h2 {
  color: var(--common-text-color-heavy);
  font-weight: 700;
  margin: 0;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .module-info-card {
    border-radius: 16px;
  }

  :deep(.info-label),
  :deep(.info-content) {
    padding: 10px 12px !important;
  }

  .tag-item {
    height: 24px;
    line-height: 22px;
    padding: 0 10px;
    font-size: 12px;
  }

  h2 {
    font-size: 18px;
  }
}
</style>
