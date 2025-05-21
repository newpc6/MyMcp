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
          
          <el-descriptions-item v-if="moduleInfo.author" label="作者" label-class-name="info-label" content-class-name="info-content">
            {{ moduleInfo.author }}
          </el-descriptions-item>
          <el-descriptions-item v-if="moduleInfo.version" label="版本" label-class-name="info-label" content-class-name="info-content">
            {{ moduleInfo.version }}
          </el-descriptions-item>
          <el-descriptions-item v-if="moduleInfo.creator_name" label="创建者" label-class-name="info-label" content-class-name="info-content">
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

.module-info-descriptions {
  margin-top: 10px;
}

:deep(.info-label) {
  background: rgba(245, 250, 255, 0.7);
  color: #303133;
  font-weight: 600;
}

:deep(.info-content) {
  color: #606266;
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