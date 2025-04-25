<template>
  <el-container v-loading="loading" class="p-4">
    <el-main class="p-0">
      <el-alert
        v-if="error && !loading"
        :title="'加载错误: ' + error"
        type="error"
        show-icon
        class="mb-4"
        :closable="false"
      />

      <!-- MCP 服务管理面板 -->
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="flex justify-between items-center">
            <span class="text-lg font-semibold">MCP 服务状态</span>
            <div>
              <el-button type="primary" size="small" @click="refreshMcpStatus">刷新</el-button>
              <el-button 
                type="warning" 
                size="small" 
                @click="restartMcp"
                :loading="restarting"
              >重启服务</el-button>
              <el-button
                type="primary"
                size="small"
                @click="showSseSettingsModal = true"
              >SSE 设置</el-button>
            </div>
          </div>
        </template>
        
        <el-descriptions :column="3" border>
          <el-descriptions-item label="运行状态">
            <el-tag :type="mcpStatus.running ? 'success' : 'danger'">
              {{ mcpStatus.running ? '运行中' : '未运行' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="SSE URL">
            {{ mcpStatus.sse_url || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="SSE 连接">
            <el-tag :type="sseConnected ? 'success' : 'danger'">
              {{ sseConnected ? '已连接' : '未连接' }}
            </el-tag>
            <el-button 
              type="primary" 
              size="small" 
              class="ml-2"
              @click="testSseConnection"
              :loading="testingConnection"
            >测试连接</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="端口">
            {{ mcpStatus.port || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="启用工具数">
            <el-badge :value="mcpStatus.enabled_tools_count || 0" type="primary" />
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 已启用的工具列表 -->
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="flex justify-between items-center">
            <span class="text-lg font-semibold">已启用的工具</span>
          </div>
        </template>
        
        <div v-if="mcpStatus.enabled_tools && mcpStatus.enabled_tools.length > 0">
          <el-table :data="enabledToolsTableData" border style="width: 100%">
            <el-table-column prop="index" label="#" width="60" />
            <el-table-column prop="name" label="工具名称" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="unloadToolByName(scope.row.name)"
                  :loading="unloadingTool === scope.row.name"
                >卸载</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-empty v-else description="没有启用的工具" :image-size="100" />
      </el-card>

      <!-- 工具加载区域 -->
      <el-card shadow="never">
        <template #header>
          <div class="flex justify-between items-center">
            <span class="text-lg font-semibold">动态加载工具</span>
          </div>
        </template>
        
        <el-form 
          :model="toolLoadForm"
          label-width="120px"
          @submit.prevent="loadToolFromModule"
        >
          <el-form-item label="模块路径" required>
            <el-input v-model="toolLoadForm.modulePath" placeholder="例如: repository.tavily_tool" />
          </el-form-item>
          <el-form-item label="函数名称" required>
            <el-input v-model="toolLoadForm.functionName" placeholder="例如: search_tavily" />
          </el-form-item>
          <el-form-item label="工具名称(可选)">
            <el-input v-model="toolLoadForm.toolName" placeholder="不填则使用函数名" />
          </el-form-item>
          <el-form-item label="工具描述(可选)">
            <el-input v-model="toolLoadForm.description" placeholder="工具描述" />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="loadToolFromModule"
              :loading="loadingTool"
            >加载工具</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-main>

    <!-- SSE设置对话框 -->
    <el-dialog
      v-model="showSseSettingsModal"
      title="MCP SSE 设置"
      width="50%"
      :close-on-click-modal="false"
    >
      <el-form label-position="top">
        <el-form-item label="SSE URL" required>
          <el-input v-model="sseUrlForm.url" placeholder="例如: http://localhost:8002/sse" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSseSettingsModal = false">取消</el-button>
          <el-button type="primary" @click="updateSseUrl" :loading="updatingSseUrl">
            保存
          </el-button>
          <el-button type="success" @click="testSseConnectionWithUrl" :loading="testingConnection">
            测试连接
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { 
  getMcpStatus, getEnabledTools, restartMcpService, 
  loadTool, unloadTool, updateSseUrl as updateSseUrlApi,
  testMcpSseConnection
} from '../../api/mcp';
import {
  ElContainer, ElMain, ElCard, ElButton, ElTag, ElBadge,
  ElDescriptions, ElDescriptionsItem, ElForm, ElFormItem,
  ElInput, ElDivider, ElDialog, ElAlert, ElMessage, ElEmpty,
  ElTable, ElTableColumn
} from 'element-plus';

// 状态变量
const loading = ref(false);
const error = ref<string | null>(null);

// MCP服务状态相关变量
const mcpStatus = ref<any>({
  running: false,
  port: null,
  sse_url: '',
  enabled_tools_count: 0,
  enabled_tools: []
});
const sseConnected = ref(false);
const restarting = ref(false);
const testingConnection = ref(false);
const showSseSettingsModal = ref(false);
const sseUrlForm = ref({ url: '' });
const updatingSseUrl = ref(false);

// 工具加载相关变量
const toolLoadForm = ref({
  modulePath: '',
  functionName: '',
  toolName: '',
  description: ''
});
const loadingTool = ref(false);
const unloadingTool = ref<string | null>(null); // 记录正在卸载的工具名称

// 已启用工具的表格数据
const enabledToolsTableData = computed(() => {
  return (mcpStatus.value.enabled_tools || []).map((toolName: string, index: number) => {
    return {
      index: index + 1,
      name: toolName
    };
  });
});

// 获取MCP服务状态
async function refreshMcpStatus() {
  loading.value = true;
  error.value = null;
  
  try {
    const data = await getMcpStatus();
    mcpStatus.value = data.data;
    // 如果SSE URL存在，更新表单
    if (mcpStatus.value.sse_url) {
      sseUrlForm.value.url = mcpStatus.value.sse_url;
    }
    // 测试连接
    await testSseConnection();
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '获取MCP状态失败';
    ElMessage.error(`获取MCP状态失败: ${error.value}`);
  } finally {
    loading.value = false;
  }
}

// 重启MCP服务
async function restartMcp() {
  restarting.value = true;
  try {
    await restartMcpService();
    ElMessage.success('MCP服务已成功重启');
    // 重新加载状态
    await refreshMcpStatus();
  } catch (err: any) {
    ElMessage.error(`重启MCP服务失败: ${err.message}`);
  } finally {
    restarting.value = false;
  }
}

// 测试SSE连接
async function testSseConnection() {
  testingConnection.value = true;
  try {
    const url = mcpStatus.value.sse_url;
    if (!url) {
      ElMessage.warning('SSE URL未设置');
      sseConnected.value = false;
      return;
    }
    
    const data = await testMcpSseConnection(url);
    sseConnected.value = data.code === 0;
    if (data.code === 0) {
      ElMessage.success('连接测试成功');
    } else {
      ElMessage.error(`连接测试失败: ${data.message}`);
    }
  } catch (err: any) {
    sseConnected.value = false;
    ElMessage.error(`测试连接失败: ${err.message}`);
  } finally {
    testingConnection.value = false;
  }
}

// 使用表单中的URL测试连接
async function testSseConnectionWithUrl() {
  testingConnection.value = true;
  try {
    const url = sseUrlForm.value.url;
    if (!url) {
      ElMessage.warning('请输入SSE URL');
      return;
    }
    
    const data = await testMcpSseConnection(url);
    sseConnected.value = data.code === 0;
    if (data.code === 0) {
      ElMessage.success('连接测试成功');
    } else {
      ElMessage.error(`连接测试失败: ${data.message}`);
    }
  } catch (err: any) {
    ElMessage.error(`测试连接失败: ${err.message}`);
  } finally {
    testingConnection.value = false;
  }
}

// 更新SSE URL
async function updateSseUrl() {
  updatingSseUrl.value = true;
  try {
    const url = sseUrlForm.value.url;
    if (!url) {
      ElMessage.warning('请输入SSE URL');
      return;
    }
    
    await updateSseUrlApi(url);
    ElMessage.success('SSE URL已更新');
    showSseSettingsModal.value = false;
    // 刷新状态
    await refreshMcpStatus();
  } catch (err: any) {
    ElMessage.error(`更新SSE URL失败: ${err.message}`);
  } finally {
    updatingSseUrl.value = false;
  }
}

// 从模块加载工具
async function loadToolFromModule() {
  loadingTool.value = true;
  try {
    const { modulePath, functionName, toolName, description } = toolLoadForm.value;
    
    if (!modulePath || !functionName) {
      ElMessage.warning('请输入模块路径和函数名称');
      return;
    }
    
    await loadTool(modulePath, functionName, toolName, description);
    ElMessage.success(`工具 ${toolName || functionName} 已成功加载`);
    
    // 清空表单
    toolLoadForm.value = {
      modulePath: '',
      functionName: '',
      toolName: '',
      description: ''
    };
    
    // 刷新状态
    await refreshMcpStatus();
  } catch (err: any) {
    ElMessage.error(`加载工具失败: ${err.message || err}`);
  } finally {
    loadingTool.value = false;
  }
}

// 卸载指定名称的工具
async function unloadToolByName(toolName: string) {
  unloadingTool.value = toolName;
  try {
    await unloadTool(toolName);
    ElMessage.success(`工具 ${toolName} 已卸载`);
    // 刷新状态
    await refreshMcpStatus();
  } catch (err: any) {
    ElMessage.error(`卸载工具失败: ${err.message}`);
  } finally {
    unloadingTool.value = null;
  }
}

// 在组件挂载时获取MCP状态
onMounted(() => {
  console.log('MCP status component mounted');
  refreshMcpStatus();
});
</script>

<style scoped>
.el-container {
  min-height: calc(100vh - 50px);
}

.el-card {
  margin-bottom: 20px;
}

.el-card:last-child {
  margin-bottom: 0;
}

.el-descriptions {
  margin-bottom: 16px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.width-full {
  width: 100%;
}
</style> 