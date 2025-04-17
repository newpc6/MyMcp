<template>
  <el-container v-loading="loading" class="p-4">
    <!-- <el-header height="auto" class="mb-4">
      <h1 class="text-2xl font-bold">MCP 工具管理</h1>
    </el-header> -->

    <el-main class="p-0">
      <el-alert
        v-if="error && !loading"
        :title="'加载错误: ' + error"
        type="error"
        show-icon
        class="mb-4"
        :closable="false"
      />

      <el-row :gutter="20">
        <!-- 工具列表 -->
        <el-col :xs="24" :sm="10" :md="8">
          <el-card shadow="never">
            <template #header>
              <div class="flex justify-between items-center">
                <div class="flex-between width-full">
                    <span class="text-lg font-semibold">工具列表</span>
                    <div>
                        <el-button type="primary" size="small" @click="fetchTools">
                        刷新
                        </el-button>
                        <el-button type="primary" size="small" @click="showCreateModal = true">
                        新建工具
                        </el-button>
                    </div>
                </div>
              </div>
            </template>
            <div v-if="moduleList.length > 0" class="tool-module-list">
              <!-- 直接列出所有模块，不使用折叠面板 -->
              <div v-for="module in moduleList" :key="module.module_name" class="module-section">
                <!-- 模块标题，点击后编辑文件 -->
                <div class="module-header" @click="handleEditModule(module.module_name)">
                  <div class="flex-between width-full">
                    <div class="flex items-center">
                      <el-icon class="mr-2"><Document /></el-icon>
                      <span class="font-medium">{{ formatModuleName(module.module_name) }}</span>
                      <el-tag size="small" type="info" class="ml-2" round>{{ module.tools.length }}</el-tag>
                    </div>
                    <el-button type="primary" size="small" @click.stop="handleEditModule(module.module_name)">
                      编辑模块
                    </el-button>
                  </div>
                </div>

                <!-- 模块下的工具列表 -->
                <div class="tools-list">
                  <div 
                    v-for="tool in module.tools" 
                    :key="tool.file_path" 
                    class="tool-item"
                  >
                  <el-form label-width="80px">
                    <el-form-item label="工具名称">
                        <el-tag size="small" type="success" class="ml-2">{{ tool.name }}</el-tag>
                    </el-form-item>
                    <el-form-item label="工具描述">
                        <el-text class="text-sm text-gray-600" truncated>{{ tool.doc || '暂无描述' }}</el-text>
                    </el-form-item>
                    <el-form-item label="参数">
                        <div v-if="tool.parameters && Object.keys(tool.parameters).length > 0">
                            <el-table :data="formatParameters(tool.parameters)" border size="small" class="parameter-table">
                                <el-table-column prop="name" label="参数名称" width="120" />
                                <el-table-column prop="type" label="类型">
                                    <template #default="scope">
                                        <el-tag size="small" type="info">{{ scope.row.type }}</el-tag>
                                    </template>
                                </el-table-column>
                                <el-table-column prop="default" label="默认值">
                                    <template #default="scope">
                                        <code v-if="scope.row.default !== undefined">{{ scope.row.default }}</code>
                                        <span v-else class="text-gray-400">-</span>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                        <div v-else>
                            <el-tag size="small" type="info" class="ml-2">无参数</el-tag>
                        </div>
                    </el-form-item>
                    <el-form-item label="返回类型">
                        <el-tag size="small" type="primary" class="ml-2">{{ tool.return_type }}</el-tag>
                    </el-form-item>
                    <el-form-item label="操作">
                        <el-button type="primary" size="small" @click="handleDebugTool(tool)">调试</el-button>
                    </el-form-item>
                  </el-form>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="没有找到工具。" :image-size="100" />
          </el-card>
        </el-col>

        <!-- 工具详情/编辑器 -->
        <el-col :xs="24" :sm="14" :md="16">
          <el-card shadow="never" class="h-full flex flex-col">
            <div v-if="selectedToolPath">
              <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-semibold">{{ selectedToolPath }}</h2>
                <!-- 添加标签切换 -->
                <el-radio-group v-model="activeTab" size="small">
                  <el-radio-button label="editor">编辑代码</el-radio-button>
                  <el-radio-button label="debug">调试工具</el-radio-button>
                </el-radio-group>
              </div>

              <!-- 编辑器面板 -->
              <div v-if="activeTab === 'editor'">
                <div v-if="loading && !selectedToolContent" class="text-gray-500">加载内容...</div>
                <div v-else-if="error && !selectedToolContent" class="text-red-500">加载内容失败</div>
                <div v-else>
                  <el-input
                    v-model="editableContent"
                    type="textarea"
                    :rows="28"
                    placeholder="工具代码..."
                    class="font-mono text-sm flex-grow"
                    resize="none"
                  />
                  <div class="mt-3 text-right space-x-2">
                    <el-button
                      type="success"
                      @click="saveToolChanges"
                      :disabled="!isContentChanged || loading"
                    >
                      保存更改
                    </el-button>
                    <el-button
                      type="danger"
                      @click="confirmDeleteTool"
                      :disabled="loading"
                    >
                      删除工具
                    </el-button>
                  </div>
                </div>
              </div>
              
              <!-- 调试面板 -->
              <div v-else-if="activeTab === 'debug' && selectedToolInfo">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="工具名称">{{ selectedToolInfo.name }}</el-descriptions-item>
                  <el-descriptions-item label="工具描述">{{ selectedToolInfo.doc || '暂无描述' }}</el-descriptions-item>
                  <el-descriptions-item label="返回类型">
                    <el-tag size="small" type="primary">{{ selectedToolInfo.return_type }}</el-tag>
                  </el-descriptions-item>
                </el-descriptions>
                
                <!-- 调试参数表单 -->
                <el-form
                  label-width="120px"
                  class="debug-form mt-4"
                >
                  <el-form-item
                    v-for="(param, name) in selectedToolInfo.parameters"
                    :key="name"
                    :label="String(name)"
                  >
                    <div class="flex items-center">
                      <el-input
                        v-if="param.type === 'str'"
                        v-model="debugForm[name]"
                        :placeholder="`输入${name}`"
                      />
                      <el-input-number
                        v-else-if="param.type === 'int' || param.type === 'integer'"
                        v-model="debugForm[name]"
                        :placeholder="`输入${name}`"
                      />
                      <el-input-number
                        v-else-if="param.type === 'float' || param.type === 'number'"
                        v-model="debugForm[name]"
                        :placeholder="`输入${name}`"
                        :step="0.1"
                      />
                      <el-switch
                        v-else-if="param.type === 'bool' || param.type === 'boolean'"
                        v-model="debugForm[name]"
                      />
                      <el-input
                        v-else
                        v-model="debugForm[name]"
                        :placeholder="`输入${name} (${param.type})`"
                      />
                      <el-tag size="small" type="info" class="ml-2">{{ param.type }}</el-tag>
                    </div>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="executeInlineTool" :loading="executing">
                      执行
                    </el-button>
                  </el-form-item>
                </el-form>
                
                <!-- 执行结果 -->
                <div v-if="executionError || executionResult !== null" class="result-section">
                  <el-divider content-position="left">执行结果</el-divider>
                  
                  <div v-if="executionError" class="error-result mb-4">
                    <el-alert
                      :title="'执行错误'"
                      type="error"
                      show-icon
                      :closable="false"
                    >
                      <p>{{ executionError }}</p>
                    </el-alert>
                  </div>
                  
                  <pre v-else class="result-content">{{ typeof executionResult === 'object' ? JSON.stringify(executionResult, null, 2) : String(executionResult) }}</pre>
                </div>
              </div>
            </div>
            <el-empty v-else description="请从左侧选择一个工具进行编辑或调试。" :image-size="150" class="flex-grow" />
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- 新建工具 Dialog -->
    <el-dialog
      v-model="showCreateModal"
      title="创建新工具"
      width="60%"
      :close-on-click-modal="false"
      @closed="resetCreateForm"
    >
      <el-form ref="createFormRef" :model="newTool" label-position="top" @submit.prevent="handleCreateTool">
        <el-form-item label="文件路径 (例如: my_tools/tool.py)" prop="path" :rules="[{ required: true, message: '请输入文件路径', trigger: 'blur' }]">
          <el-input v-model="newTool.path" placeholder="例如: my_tools/new_tool.py" />
        </el-form-item>
        <el-form-item label="初始内容" prop="content" :rules="[{ required: true, message: '请输入初始内容', trigger: 'blur' }]">
          <el-input
            v-model="newTool.content"
            type="textarea"
            :rows="10"
            class="font-mono text-sm"
            placeholder="# Your Python tool code here
from repository.mcp_base import mcp

@mcp.tool(...)
def my_new_tool(...):
    ..."
          />
        </el-form-item>
        <el-alert v-if="createError" :title="createError" type="error" show-icon class="mb-4" :closable="false" />
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateModal = false">取消</el-button>
          <el-button type="primary" @click="submitCreateForm" :loading="loading">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import type { ToolInfo, ToolCreate, ToolContent } from '../../types/tools';
import { listTools, getToolContent, createTool, updateTool, deleteTool } from '../../api/tools';
import { executeTool } from '../../api/execution';
import {
  ElContainer, ElHeader, ElMain, ElRow, ElCol, ElCard, ElButton, ElMenu, ElMenuItem,
  ElInput, ElEmpty, ElDialog, ElForm, ElFormItem, ElAlert, ElMessage, ElMessageBox,
  ElTag, ElCollapse, ElCollapseItem, ElTable, ElTableColumn, ElInputNumber, ElSwitch,
  ElButtonGroup, ElText, ElDescriptions, ElDescriptionsItem, ElDivider, ElRadioGroup,
  ElRadioButton
} from 'element-plus';
import {
  Document,
  List,
  Right,
} from '@element-plus/icons-vue';
import type { FormInstance } from 'element-plus';

// 状态变量
const loading = ref(false);
const error = ref<string | null>(null);
const moduleList = ref<any[]>([]);
const selectedToolPath = ref<string | null>(null);
const selectedToolContent = ref<string | null>(null);
const editableContent = ref('');
const showCreateModal = ref(false);
const newTool = ref<ToolCreate>({ path: '', content: '' });
const createError = ref<string | null>(null);
const createFormRef = ref<FormInstance>();
const activeTab = ref('editor');

// 调试相关变量
const executing = ref(false);
const debugForm = ref<Record<string, any>>({});
const executionResult = ref<any>(null);
const executionError = ref<string | null>(null);

// 格式化模块名称，只显示最后一部分
function formatModuleName(moduleName: string): string {
  const parts = moduleName.split('.');
  return parts[parts.length - 1] || moduleName;
}

// 格式化参数为表格数据
function formatParameters(parameters: Record<string, any>): Array<{name: string, type: string, default: any}> {
  return Object.entries(parameters).map(([key, value]) => {
    return {
      name: key,
      type: value.type || 'Any',
      default: value.default
    };
  });
}

// 获取工具列表
async function fetchTools() {
  loading.value = true;
  error.value = null;
  try {
    moduleList.value = await listTools();
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '加载工具列表失败';
    moduleList.value = []; // 清空防止显示旧数据
  } finally {
    // loading.value = false;
  }
  setTimeout(() => {
    loading.value = false;
  }, 0.5 * 1000)
}

// 获取工具内容
async function fetchToolContent(path: string) {
  if (!path) return;
  
  loading.value = true;
  error.value = null;
  selectedToolContent.value = null; // 清空旧内容
  
  try {
    const result = await getToolContent(path);
    selectedToolContent.value = result.content;
    editableContent.value = result.content;
  } catch (err: any) {
    const errorDetail = err.response?.data?.detail || err.message;
    error.value = `加载工具内容失败: ${errorDetail}`;
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
}

// 选择工具
function handleSelectTool(path: string) {
  if (selectedToolPath.value !== path) {
    selectedToolPath.value = path;
    // 切换到编辑标签页
    activeTab.value = 'editor';
    fetchToolContent(path);
  }
}

// 编辑模块
function handleEditModule(moduleName: string) {
  // 查找该模块的第一个工具的文件路径
  for (const module of moduleList.value) {
    if (module.module_name === moduleName && module.tools.length > 0) {
      // 显示模块的第一个工具，但不将工具设为选中状态
      selectedToolPath.value = module.tools[0].file_path;
      // 切换到编辑标签页
      activeTab.value = 'editor';
      fetchToolContent(module.tools[0].file_path);
      return;
    }
  }
  
  ElMessage.warning(`模块 ${moduleName} 没有可编辑的工具`);
}

// 调试工具
function handleDebugTool(tool: any) {
  console.log('调试工具', tool);
  // 选择工具并切换到调试标签页
  selectedToolPath.value = tool.file_path;
  selectedToolInfo.value.name = tool.name;
  selectedToolInfo.value.doc = tool.doc;
  selectedToolInfo.value.return_type = tool.return_type;
  selectedToolInfo.value.parameters = tool.parameters;
  // 清空之前的调试表单和结果
  debugForm.value = {};
  executionResult.value = null;
  executionError.value = null;
  
  // 直接使用传入的tool对象设置默认值
  if (tool.parameters) {
    Object.entries(tool.parameters).forEach(([name, param]: [string, any]) => {
      if (param.default !== undefined) {
        debugForm.value[name] = param.default;
      }
    });
  }
  
  // 切换到调试标签页
  activeTab.value = 'debug';
  
  // 获取工具内容（如果需要的话）
  // fetchToolContent(tool.file_path);
}

// 执行内联工具
async function executeInlineTool() {
  if (!selectedToolInfo.value) return;
  
  executing.value = true;
  executionError.value = null;
  
  try {
    // 使用API服务执行工具
    const data = await executeTool({
      tool_name: selectedToolInfo.value.name,
      parameters: debugForm.value
    });
    
    executionResult.value = data.result;
    executionError.value = null;
  } catch (err: any) {
    executionError.value = err.response?.data?.detail || err.message || '执行工具时发生错误';
  } finally {
    executing.value = false;
  }
}

// 保存工具更改
async function saveToolChanges() {
  if (!selectedToolPath.value || !isContentChanged.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    await updateTool(selectedToolPath.value, { content: editableContent.value });
    ElMessage.success('工具已成功更新！');
    selectedToolContent.value = editableContent.value; // 更新当前内容
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '更新失败';
    ElMessage.error(`更新失败: ${error.value}`);
  } finally {
    loading.value = false;
  }
}

// 删除工具
async function confirmDeleteTool() {
  if (!selectedToolPath.value) return;
  
  try {
    await ElMessageBox.confirm(
      `确定要删除工具 ${selectedToolPath.value} 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    loading.value = true;
    error.value = null;
    
    try {
      await deleteTool(selectedToolPath.value);
      ElMessage.success('工具已成功删除！');
      
      // 清除选中工具
      selectedToolPath.value = null;
      selectedToolContent.value = null;
      editableContent.value = '';
      
      // 重新加载工具列表
      await fetchTools();
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || '删除失败';
      ElMessage.error(`删除失败: ${error.value}`);
    } finally {
      loading.value = false;
    }
  } catch {
    // 用户取消删除
    ElMessage.info('删除操作已取消');
  }
}

// 创建新工具
async function handleCreateTool() {
  createError.value = null;
  loading.value = true;
  
  try {
    await createTool(newTool.value);
    showCreateModal.value = false;
    ElMessage.success('工具已成功创建！');
    
    // 重新加载工具列表
    await fetchTools();
  } catch (err: any) {
    createError.value = err.response?.data?.detail || err.message || '创建工具时发生未知错误';
  } finally {
    loading.value = false;
  }
}

// 表单验证并提交
async function submitCreateForm() {
  if (!createFormRef.value) return;
  
  createFormRef.value.validate(async (valid) => {
    if (valid) {
      await handleCreateTool();
    } else {
      console.log('表单验证失败!');
    }
  });
}

// 重置创建表单
function resetCreateForm() {
  if (createFormRef.value) {
    createFormRef.value.resetFields();
  }
  newTool.value = { path: '', content: '' };
  createError.value = null;
}

// 计算内容是否变化
const isContentChanged = computed(() => {
  return editableContent.value !== (selectedToolContent.value ?? '');
});

// 当选中工具路径变化时，清空编辑器内容
watch(() => selectedToolPath.value, (newPath) => {
  if (!newPath) {
    editableContent.value = '';
  } else {
    // 重置调试表单
    debugForm.value = {};
    executionResult.value = null;
    executionError.value = null;
    
    // 如果当前在调试标签页，为参数设置默认值
    if (activeTab.value === 'debug' && selectedToolInfo.value?.parameters) {
      Object.entries(selectedToolInfo.value.parameters).forEach(([name, param]: [string, any]) => {
        if (param.default !== undefined) {
          debugForm.value[name] = param.default;
        }
      });
    }
  }
});

// 监听标签页切换
watch(() => activeTab.value, (newTab) => {
  if (newTab === 'debug' && selectedToolInfo.value?.parameters) {
    // 重置调试表单
    debugForm.value = {};
    executionResult.value = null;
    executionError.value = null;
    
    // 为参数设置默认值
    Object.entries(selectedToolInfo.value.parameters).forEach(([name, param]: [string, any]) => {
      if (param.default !== undefined) {
        debugForm.value[name] = param.default;
      }
    });
  }
});

// 获取当前选中工具的信息
const selectedToolInfo = computed(() => {
  if (!selectedToolPath.value) return null;
  
  // 在所有模块中查找匹配的工具
  for (const module of moduleList.value) {
    for (const tool of module.tools) {
      if (tool.file_path === selectedToolPath.value) {
        return tool;
      }
    }
  }
  return null;
});

// 在组件挂载时获取工具列表
onMounted(() => {
  console.log('Tools component mounted');
  fetchTools();
});
</script>

<style scoped>
.el-container {
  min-height: calc(100vh - 50px); /* 假设顶部导航栏高度为 50px */
}
.el-card {
   display: flex;
   flex-direction: column;
   height: 100%; /* 让卡片占满 el-col 的高度 */
 }
 .el-card :deep(.el-card__body) {
   flex-grow: 1; /* 让卡片主体区域能够扩展 */
   display: flex;
   flex-direction: column;
 }

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 100%;
  min-height: 200px; /* 给菜单一个最小高度 */
}

/* 确保 el-menu-item 内容不换行并显示省略号 */
.el-menu-item > div {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

/* 确保编辑器填满空间 */
.el-textarea {
  flex-grow: 1;
}
.el-textarea :deep(textarea) {
  height: 100% !important;
}

/* 微调对话框表单项间距 */
.el-dialog .el-form-item {
  margin-bottom: 18px;
}

.tool-item {
  border: 1px solid var(--el-border-color-lighter);
  padding: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background-color 0.3s;
}

.tool-item:last-child {
  border-bottom: none;
}

.tool-item:hover {
  background-color: var(--el-color-primary-light-9);
}

.tool-item.is-active {
  background-color: var(--el-color-primary-light-8);
}

.tool-content {
  margin-bottom: 8px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.tool-doc {
  width: 100%;
  line-height: 1.4;
  margin-bottom: 8px;
}

.tool-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tool-tag {
  display: flex;
  align-items: center;
  font-size: 11px;
}

.tool-actions {
  display: flex;
  justify-content: flex-start;
}

/* 模块部分样式 */
.module-section {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.module-header {
  background-color: var(--el-color-primary-light-9);
  padding: 12px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.module-header:hover {
  background-color: var(--el-color-primary-light-8);
}

.tools-list {
  padding: 8px 0;
  background-color: var(--el-bg-color);
}

/* 工具模块列表样式 */
.tool-module-list {
  padding: 8px;
  height: 70vh;
  overflow-y: auto;
}

/* 工具参数表格样式 */
.tool-details {
  padding: 10px;
  font-size: 13px;
}

:deep(.el-table--small) {
  font-size: 12px;
}

:deep(.el-table th) {
  background-color: var(--el-color-info-light-9);
  color: var(--el-color-info-dark-2);
  font-weight: 600;
}

/* 美化参数面板 */
:deep(.el-collapse-item.is-active .el-collapse-item__header) {
  color: var(--el-color-primary);
}

/* 确保内容区域足够高 */
.el-card {
  min-height: 500px;
}

/* 调试表单样式 */
.debug-form {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

/* 结果内容样式 */
.result-content {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-result {
  max-height: 400px;
  overflow-y: auto;
}

.parameter-table {
  width: 100%;
  margin-bottom: 8px;
}

.text-gray-400 {
  color: #9ca3af;
}

code {
  background: var(--el-fill-color-light);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}

/* 确保表格内容紧凑 */
.parameter-table :deep(.el-table__cell) {
  padding: 4px 8px;
}

/* 调整表格宽度以适应容器 */
.parameter-table :deep(.el-table__body),
.parameter-table :deep(.el-table__header) {
  width: 100% !important;
}

/* 调试区域样式 */
.debug-section {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* 结果区域样式 */
.result-section {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style> 