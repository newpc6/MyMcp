<template>
  <el-container class="p-4">
    <el-main class="p-0">
      <el-card class="mb-4" shadow="never">
        <template #header>
          <div class="flex justify-between items-center">
            <div class="flex items-center">
              <el-icon class="mr-2"><Tools /></el-icon>
              <span class="text-lg font-semibold">MCP 广场</span>
            </div>
            <div>
              <el-button 
                type="primary" 
                @click="scanModules" 
                :loading="scanning"
              >扫描并更新模块</el-button>
            </div>
          </div>
        </template>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <el-card 
            v-for="module in modules" 
            :key="module.id" 
            class="module-card cursor-pointer" 
            shadow="hover"
            @click="goToModuleDetail(module.id)"
          >
            <div class="flex items-start">
              <el-avatar 
                :icon="getModuleIcon(module)"
                :size="50"
                class="mr-4"
              ></el-avatar>
              <div class="flex-1">
                <h3 class="text-lg font-medium mb-1">{{ module.name }}</h3>
                <p class="text-gray-500 mb-2 text-sm line-clamp-2">{{ module.description }}</p>
                <div class="flex justify-between items-center">
                  <div>
                    <el-tag size="small" type="info" class="mr-1">
                      {{ module.tools_count }} 个工具
                    </el-tag>
                    <el-tag 
                      size="small" 
                      :type="module.is_hosted ? 'success' : 'primary'"
                    >
                      {{ module.is_hosted ? '托管' : '本地' }}
                    </el-tag>
                  </div>
                  <el-button type="primary" size="small" @click.stop="goToModuleDetail(module.id)">
                    查看详情
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <div v-if="modules.length === 0 && !loading" class="text-center py-10">
          <el-empty description="暂无MCP模块" />
          <el-button type="primary" @click="scanModules" class="mt-4">扫描并添加模块</el-button>
        </div>
        
        <div v-if="loading" class="py-20">
          <el-skeleton :rows="6" animated />
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElNotification } from 'element-plus';
import { Tools } from '@element-plus/icons-vue';
import { listModules, scanModules as apiScanModules } from '../../api/marketplace';
import type { McpModuleInfo, ScanResult } from '../../types/marketplace';

const router = useRouter();
const modules = ref<McpModuleInfo[]>([]);
const loading = ref(true);
const scanning = ref(false);

// 加载模块列表
async function loadModules() {
  loading.value = true;
  try {
    modules.value = await listModules();
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

// 扫描并更新模块
async function scanModules() {
  scanning.value = true;
  try {
    const result = await apiScanModules() as ScanResult;
    ElNotification({
      title: '成功',
      message: `扫描完成: 新增${result.new_modules}个模块, ${result.new_tools}个工具`,
      type: 'success'
    });
    // 重新加载列表
    await loadModules();
  } catch (error) {
    console.error("扫描模块失败", error);
    ElNotification({
      title: '错误',
      message: '扫描MCP模块失败',
      type: 'error'
    });
  } finally {
    scanning.value = false;
  }
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
  router.push(`/marketplace/module/${moduleId}`);
}

// 页面加载时获取模块列表
onMounted(() => {
  loadModules();
});
</script>

<style scoped>
.module-card {
  transition: all 0.3s;
}
.module-card:hover {
  transform: translateY(-5px);
}
</style> 