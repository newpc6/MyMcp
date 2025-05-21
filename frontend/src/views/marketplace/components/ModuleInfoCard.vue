<template>
  <el-card class="module-info-card" shadow="never">
    <div class="flex items-start">
      <el-avatar :icon="getModuleIcon(moduleInfo)" :size="64" class="mr-6"></el-avatar>
      <div class="flex-1">
        <div class="flex justify-between">
          <h2 class="text-xl font-bold mb-2">{{ moduleInfo.name }}</h2>
          <div>
            <el-button type="primary" @click="$emit('edit')" class="mr-2" v-if="hasEditPermission">编辑</el-button>
            <el-button type="danger" @click="$emit('delete')" class="mr-2" v-if="hasEditPermission">删除</el-button>
            <el-button @click="$emit('back')" class="return-btn">返回广场</el-button>
          </div>
        </div>

        <div class="flex justify-between">
          <div class="flex-1 mr-6">
            <p class="text-gray-600 mb-4">{{ moduleInfo.description }}</p>

            <div class="flex flex-wrap mb-3">
              <el-tag v-for="tag in tags" :key="tag" size="small" class="mr-1 tag-item">{{ tag }}</el-tag>
              <el-tag size="small" :type="moduleInfo.is_hosted ? 'success' : 'primary'" class="tag-item">
                {{ moduleInfo.is_hosted ? '托管' : '本地' }}
              </el-tag>
              <el-tag size="small" type="info" class="tag-item">
                {{ moduleInfo.tools_count }} 个工具
              </el-tag>
            </div>
          </div>

          <div class="module-info-meta">
            <div v-if="moduleInfo.author" class="module-meta-item"><strong>作者:</strong> {{ moduleInfo.author }}</div>
            <div v-if="moduleInfo.version" class="module-meta-item"><strong>版本:</strong> {{ moduleInfo.version }}</div>
            <div v-if="moduleInfo.creator_name" class="module-meta-item"><strong>创建者:</strong> {{ moduleInfo.creator_name }}</div>
            <div class="module-meta-item">
              <strong>状态:</strong>
              <el-tag size="small" :type="moduleInfo.is_public ? 'success' : 'danger'" class="ml-1">
                {{ moduleInfo.is_public ? '公开' : '私有' }}
              </el-tag>
            </div>
            <div class="module-meta-item"><strong>创建时间:</strong> {{ moduleInfo.created_at }}</div>
            <div class="module-meta-item"><strong>更新时间:</strong> {{ moduleInfo.updated_at }}</div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { McpModuleInfo } from '../../types/marketplace';

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
    return props.moduleInfo.tags.split(',').filter(t => t.trim());
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

<style scoped>
.module-info-card {
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  transition: all 0.3s ease;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff, #f8fcff);
}

.module-info-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12) !important;
  transform: translateY(-2px);
}

.module-info-meta {
  background: rgba(245, 250, 255, 0.7);
  padding: 12px 16px;
  border-radius: 12px;
  min-width: 220px;
  border: 1px solid rgba(220, 240, 255, 0.8);
}

.module-meta-item {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.module-meta-item strong {
  color: #303133;
  margin-right: 4px;
}

.return-btn {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.tag-item {
  border-radius: 20px;
  padding: 0 12px;
  height: 24px;
  line-height: 22px;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.tag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}
</style> 