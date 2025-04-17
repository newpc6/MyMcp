<template>
  <div class="container mx-auto p-4">
    <el-card class="mb-4" shadow="always">
      <template #header>
        <div class="flex justify-between items-center">
          <div class="flex items-center">
            <el-icon class="mr-2"><Connection /></el-icon>
            <h1 class="text-xl font-bold">MCP 模块管理</h1>
          </div>
          <el-button 
            type="primary" 
            @click="showCreateModal = true" 
            :icon="Plus"
            size="small"
          >
            新建模块
          </el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 模块列表 -->
        <el-col :span="8">
          <el-card shadow="hover" class="module-list-card">
            <template #header>
              <div class="flex justify-between items-center">
                <span class="font-medium flex items-center">
                  <el-icon class="mr-1"><Grid /></el-icon>模块列表
                </span>
                <el-tag type="info" size="small" v-if="moduleStore.modules.length > 0">
                  {{ moduleStore.modules.length }} 个模块
                </el-tag>
              </div>
            </template>

            <el-skeleton :rows="4" animated v-if="moduleStore.loading && !moduleStore.modules.length" />
            
            <el-alert
              v-else-if="moduleStore.error"
              :title="moduleStore.error"
              type="error"
              show-icon
              :closable="false"
              class="mb-4"
            />

            <el-empty description="没有找到模块" v-else-if="moduleStore.modules.length === 0" />

            <el-scrollbar height="450px" v-else>
              <el-menu
                class="module-menu"
                :default-active="moduleStore.selectedModulePath"
              >
                <el-menu-item
                  v-for="module in moduleStore.modules"
                  :key="module.path"
                  :index="module.path"
                  @click="selectModule(module.path)"
                >
                  <template #title>
                    <span class="font-medium">{{ module.name }}</span>
                    <el-tag size="small" type="info" class="ml-2">{{ module.path }}</el-tag>
                  </template>
                </el-menu-item>
              </el-menu>
            </el-scrollbar>
          </el-card>
        </el-col>

        <!-- 模块详情/编辑器 -->
        <el-col :span="16">
          <el-card shadow="hover" class="h-full editor-card">
            <template #header>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <el-icon class="mr-1"><Edit /></el-icon>
                  <span v-if="moduleStore.selectedModulePath">
                    编辑模块: <el-tag size="small" type="success">{{ moduleStore.selectedModulePath }}</el-tag>
                  </span>
                  <span v-else>模块编辑器</span>
                </div>
                <div class="flex space-x-2" v-if="moduleStore.selectedModulePath">
                  <el-button
                    type="success"
                    size="small"
                    :icon="Check"
                    @click="saveModuleChanges"
                    :disabled="!isContentChanged || moduleStore.loading"
                    :loading="moduleStore.loading && isContentChanged"
                  >
                    保存
                  </el-button>
                  <el-popconfirm
                    title="确定要删除此模块吗？此操作不可恢复！"
                    @confirm="deleteModule"
                    confirm-button-text="确定"
                    cancel-button-text="取消"
                    confirm-button-type="danger"
                  >
                    <template #reference>
                      <el-button
                        type="danger"
                        size="small"
                        :icon="Delete"
                        :disabled="moduleStore.loading"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-popconfirm>
                </div>
              </div>
            </template>

            <el-skeleton :rows="10" animated v-if="moduleStore.loading && !moduleStore.selectedModuleContent && moduleStore.selectedModulePath" />
            
            <div v-else-if="moduleStore.selectedModulePath">
              <el-input
                v-model="editableContent"
                type="textarea"
                :rows="20"
                resize="none"
                class="code-editor"
                font-family="monospace"
              />
            </div>
            
            <div v-else class="h-80 flex flex-col items-center justify-center text-gray-400 empty-editor">
              <el-icon class="text-5xl mb-4"><Document /></el-icon>
              <p>请从左侧选择一个模块进行编辑</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 新建模块 Dialog -->
    <el-dialog
      v-model="showCreateModal"
      title="创建新模块"
      width="50%"
      destroy-on-close
    >
      <el-form :model="newModule" label-position="top">
        <el-form-item label="文件路径" required>
          <el-input 
            v-model="newModule.path" 
            placeholder="例如: my_modules/module.py"
            clearable
          >
            <template #prefix>
              <el-icon><Folder /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="初始内容" required>
          <el-input
            v-model="newModule.content"
            type="textarea"
            :rows="10"
            resize="none"
            class="code-editor"
            placeholder="# Your Python module code here
from repository.mcp_base import mcp

@mcp.module(...)
def my_new_module(...):
    ..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateModal = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleCreateModule" 
          :loading="moduleStore.loading"
        >
          创建
        </el-button>
      </template>
      
      <el-alert
        v-if="createError"
        :title="createError"
        type="error"
        show-icon
        class="mt-4"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useModuleStore } from '../../store/modules';
import type { ModuleCreate } from '../../types/modules';
import { 
  Check, 
  Delete, 
  Document, 
  Edit, 
  Connection, 
  Folder, 
  Grid,
  Plus
} from '@element-plus/icons-vue';
import { ElMessage, ElLoading } from 'element-plus';

const moduleStore = useModuleStore();

const editableContent = ref('');
const showCreateModal = ref(false);
const newModule = ref<ModuleCreate>({ path: '', content: '' });
const createError = ref<string | null>(null);

// 获取模块列表
onMounted(() => {
  moduleStore.fetchModules();
});

// 监听选中模块的变化，更新编辑器内容
watch(() => moduleStore.selectedModuleContent, (newContent) => {
  editableContent.value = newContent ?? '';
});

// 计算内容是否有变化
const isContentChanged = computed(() => {
  return editableContent.value !== (moduleStore.selectedModuleContent ?? '');
});

// 选择模块
function selectModule(modulePath: string) {
  if (moduleStore.selectedModulePath !== modulePath) {
    moduleStore.fetchModuleContent(modulePath);
  }
}

// 保存更改
async function saveModuleChanges() {
  if (!moduleStore.selectedModulePath || !isContentChanged.value) return;
  
  try {
    await moduleStore.updateModule(moduleStore.selectedModulePath, { content: editableContent.value });
    ElMessage({
      message: '模块已成功更新！',
      type: 'success',
    });
  } catch (err) {
    ElMessage.error(`更新失败: ${moduleStore.error}`);
  }
}

// 处理创建模块
async function handleCreateModule() {
  createError.value = null;
  
  if (!newModule.value.path || !newModule.value.content) {
    createError.value = '路径和内容不能为空';
    return;
  }
  
  try {
    await moduleStore.createModule(newModule.value);
    showCreateModal.value = false;
    newModule.value = { path: '', content: '' };
    ElMessage({
      message: '模块已成功创建！',
      type: 'success',
    });
  } catch (err) {
    createError.value = moduleStore.error ?? '创建模块时发生未知错误';
  }
}

// 删除模块
async function deleteModule() {
  if (!moduleStore.selectedModulePath) return;
  
  try {
    await moduleStore.deleteModule(moduleStore.selectedModulePath);
    ElMessage({
      message: '模块已成功删除！',
      type: 'success',
    });
  } catch (err) {
    ElMessage.error(`删除失败: ${moduleStore.error}`);
  }
}
</script>

<style scoped>
.module-list-card {
  height: 100%;
  transition: all 0.3s;
}

.module-menu :deep(.el-menu-item) {
  border-left: 3px solid transparent;
  margin-bottom: 4px;
  border-radius: 4px;
  height: auto;
  padding: 10px;
}

.module-menu :deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary-light-9);
  border-left-color: var(--el-color-primary);
}

.module-menu :deep(.el-menu-item:hover) {
  background-color: var(--el-color-primary-light-9);
}

.code-editor {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.code-editor :deep(textarea) {
  font-family: 'Courier New', monospace;
  padding: 10px;
}

.editor-card {
  background: linear-gradient(to bottom right, #fafafa, #f0f0f0);
  min-height: 530px;
}

.empty-editor {
  animation: pulse 2s infinite;
  opacity: 0.7;
}

@keyframes pulse {
  0% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.5;
  }
}

/* 整体科技感提升 */
:deep(.el-card) {
  border-radius: 6px;
  border: 1px solid rgba(235, 238, 245, 0.9);
  transition: all 0.3s;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

:deep(.el-card:hover) {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.08);
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(235, 238, 245, 0.7);
  padding: 12px 16px;
}
</style> 