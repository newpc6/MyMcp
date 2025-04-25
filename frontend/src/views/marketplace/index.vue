<template>
  <el-container class="marketplace-container">
    <!-- 左侧分类列表，增加宽度 -->
    <el-aside width="280px" class="pr-4">
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="flex items-center">
            <el-icon class="mr-2"><Menu /></el-icon>
            <span class="text-lg font-semibold">MCP 分类</span>
          </div>
        </template>
        
        <el-menu
          :default-active="activeCategory ? activeCategory.id.toString() : ''"
          @select="handleCategorySelect"
          class="border-0 category-menu"
        >
          <el-menu-item index="all">
            <el-icon><Collection /></el-icon>
            <span>全部</span>
          </el-menu-item>
          
          <el-menu-item 
            v-for="category in categories" 
            :key="category.id" 
            :index="category.id.toString()"
            class="category-item"
          >
            <el-icon><component :is="getCategoryIcon(category)" /></el-icon>
            <span class="category-name">{{ category.name }}</span>
            <el-tag size="small" class="ml-auto">{{ category.modules_count || 0 }}</el-tag>
          </el-menu-item>
        </el-menu>
      </el-card>
    </el-aside>
    
    <!-- 右侧内容 -->
    <el-main class="p-4">
      <el-page-header class="mb-4" :title="activeCategory && activeCategory.id !== 'all' ? activeCategory.name : 'MCP 广场'">
        <template #extra>
          <el-button 
            type="primary" 
            @click="loadModules" 
            :loading="scanning"
          >刷新</el-button>
        </template>
      </el-page-header>
      
      <!-- 一行三列的卡片网格 -->
      <div class="module-grid">
        <div v-for="module in modules" :key="module.id" class="module-item">
          <el-card 
            class="module-card" 
            shadow="hover"
            @click="goToModuleDetail(module.id)"
          >
            <div class="card-header">
              <el-avatar 
                :icon="getModuleIcon(module)"
                :size="40"
                class="mr-2"
              ></el-avatar>
              <h3 class="card-title">{{ module.name }}</h3>
            </div>
            <p class="card-desc">{{ module.description }}</p>
            <div class="card-footer">
              <div class="tag-container">
                <!-- <el-tag size="small" type="info" class="mr-1">
                  {{ module.tools_count }} 个工具
                </el-tag> -->
                <el-tag 
                  size="small" 
                  :type="module.is_hosted ? 'success' : 'primary'"
                >
                  {{ module.is_hosted ? '托管' : '本地' }}
                </el-tag>
                <el-tag 
                  v-if="module.category_name" 
                  size="small" 
                  type="warning"
                  class="ml-1"
                >
                  {{ module.category_name }}
                </el-tag>
              </div>
              <el-button type="primary" link @click.stop="goToModuleDetail(module.id)">
                查看详情
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
      
      <div v-if="modules.length === 0 && !loading" class="text-center py-10">
        <el-empty description="暂无MCP模块" />
        <el-button type="primary" @click="loadModules" class="mt-4">刷新</el-button>
      </div>
      
      <div v-if="loading" class="loading-container">
        <div class="module-grid">
          <div v-for="i in 6" :key="i" class="module-item">
            <el-skeleton class="p-4" :rows="3" animated />
          </div>
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElNotification } from 'element-plus';
import { Tools, Menu, Collection } from '@element-plus/icons-vue';
import { listModules, listCategories } from '../../api/marketplace';
import type { McpModuleInfo, ScanResult, McpCategoryInfo } from '../../types/marketplace';

const router = useRouter();
const modules = ref<McpModuleInfo[]>([]);
const categories = ref<McpCategoryInfo[]>([]);
const loading = ref(true);
const scanning = ref(false);
const selectedCategoryId = ref<string | null>('all');

const activeCategory = computed(() => {
  if (selectedCategoryId.value === 'all') {
    return { id: 'all', name: '全部' };
  }
  return categories.value.find(c => c.id.toString() === selectedCategoryId.value) || null;
});

// 加载模块列表
async function loadModules() {
  loading.value = true;
  try {
    const categoryId = selectedCategoryId.value === 'all' ? null : selectedCategoryId.value;
    const data = await listModules(categoryId);
    modules.value = data.data;
  } catch (error) {
    console.error("加载模块失败", error);
    ElNotification({
      title: '错误',
      message: '加载MCP模块列表失败',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
}

// 加载分组列表
async function loadCategories() {
  try {
    const data = await listCategories();
    categories.value = data.data;
  } catch (error) {
    console.error("加载分组失败", error);
    ElNotification({
      title: '错误',
      message: '加载MCP分组列表失败',
      type: 'error'
    });
  }
}

// 处理分组选择
function handleCategorySelect(categoryId: string) {
  selectedCategoryId.value = categoryId;
  loadModules();
}

// 根据分组类型获取图标
function getCategoryIcon(category: McpCategoryInfo) {
  // 如果分组有自定义图标，返回
  if (category.icon) {
    return category.icon;
  }
  // 默认图标
  return 'Folder';
}

// 根据模块类型获取图标
function getModuleIcon(module: McpModuleInfo) {
  // 根据模块类型或名称返回不同的图标
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

// 跳转到模块详情页
function goToModuleDetail(moduleId: number) {
  router.push(`/marketplace/${moduleId}`);
}

// 页面加载时获取模块列表和分组列表
onMounted(async () => {
  await loadCategories();
  await loadModules();
});
</script>

<style scoped>
.marketplace-container {
  height: calc(100vh - 80px);
}

.category-menu {
  max-height: calc(100vh - 150px);
  overflow-y: auto;
}

.category-item {
  display: flex;
  align-items: center;
}

.category-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 1400px) {
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1000px) {
  .module-grid {
    grid-template-columns: 1fr;
  }
}

.module-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  background-color: #fff;
  overflow: hidden;
  color: #303133;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
  box-sizing: border-box;
  padding: 20px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.module-card:hover {
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
  border-color: transparent;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  margin-bottom: 10px;
  word-break: break-all;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-desc {
  font-size: 14px;
  color: #606266;
  min-height: 42px;
  margin-bottom: 10px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 4px;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.loading-container {
  padding: 20px 0;
}

.card-icon {
  width: 42px;
  height: 42px;
  margin-right: 12px;
  border-radius: 8px;
  object-fit: cover;
}

.divider {
  height: 1px;
  background-color: #f0f2f5;
  margin: 14px 0;
}
</style> 