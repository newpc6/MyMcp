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
import type { McpModuleInfo } from '../../../types/marketplace';

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
  border-radius: 20px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(235, 235, 235, 0.6);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
  backdrop-filter: blur(10px);
  position: relative;
}

.module-info-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
  border-radius: 20px 20px 0 0;
}

/* .module-info-card:hover {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12) !important;
  transform: translateY(-6px);
} */

.module-info-descriptions {
  margin-top: 16px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(235, 235, 235, 0.6);
}

:deep(.el-descriptions__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 16px 20px;
  border-bottom: 1px solid rgba(235, 235, 235, 0.6);
}

:deep(.el-descriptions__body) {
  background: rgba(255, 255, 255, 0.8);
}

:deep(.info-label) {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%) !important;
  color: #475569 !important;
  font-weight: 600 !important;
  border-right: 1px solid rgba(235, 235, 235, 0.6) !important;
  padding: 12px 16px !important;
}

:deep(.info-content) {
  color: #64748b !important;
  padding: 12px 16px !important;
  background: rgba(255, 255, 255, 0.8) !important;
}

:deep(.el-descriptions__cell) {
  border-bottom: 1px solid rgba(235, 235, 235, 0.4) !important;
}

.return-btn {
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 10px 20px;
  font-weight: 500;
  border: 2px solid #e5e7eb;
  background: #ffffff;
  color: #6b7280;
}

.return-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

:deep(.el-button--danger) {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-button--danger:hover) {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.tag-item {
  border-radius: 20px;
  padding: 0 12px;
  height: 26px;
  line-height: 24px;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  border: 1px solid transparent;
}

.tag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-tag--success) {
  background: linear-gradient(135deg, #10b981, #059669);
  border-color: transparent;
  color: white;
}

:deep(.el-tag--primary) {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-color: transparent;
  color: white;
}

:deep(.el-tag--info) {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  border-color: transparent;
  color: white;
}

:deep(.el-tag--danger) {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border-color: transparent;
  color: white;
}

:deep(.el-tag--warning) {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-color: transparent;
  color: white;
}

:deep(.el-avatar) {
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  color: #64748b;
  border: 2px solid rgba(235, 235, 235, 0.6);
  transition: all 0.3s ease;
}

h2 {
  color: #1e293b;
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