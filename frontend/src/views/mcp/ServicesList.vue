<template>
  <el-container class="p-4">
    <el-main class="p-0">
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-bold">MCP服务管理</h2>
            <el-button type="primary" @click="refreshServices">
              <el-icon class="mr-1">
                <Refresh />
              </el-icon>刷新
            </el-button>
          </div>
        </template>

        <div v-if="loading" class="py-4">
          <el-skeleton :rows="5" animated />
        </div>
        <div v-else-if="services.length === 0" class="text-center py-8">
          <el-empty description="暂无MCP服务" :image-size="80">
            <template #description>
              <p class="text-gray-500">还没有发布任何MCP服务，可以在MCP广场发布服务</p>
            </template>
            <el-button type="primary" @click="$router.push('/marketplace')">前往MCP广场</el-button>
          </el-empty>
        </div>
        <div v-else>
          <el-table :data="services" style="width: 100%" border stripe>
            <el-table-column label="ID" prop="id" width="80" />
            <el-table-column label="模块名称" prop="module_name" min-width="120" />
            <el-table-column label="服务说明" min-width="180">
              <template #default="scope">
                <div class="flex items-center justify-between">
                  <el-tooltip :content="scope.row.description || '暂无说明'" placement="top" :show-after="500"
                    :disabled="!scope.row.description">
                    <div class="description-text truncate">
                      <span v-if="scope.row.description">{{ scope.row.description }}</span>
                      <span v-else class="text-gray-400 italic">暂无说明</span>
                    </div>
                  </el-tooltip>
                  <el-button type="primary" link size="small" @click="editServiceDescription(scope.row)" title="编辑说明">
                    <el-icon>
                      <Edit />
                    </el-icon>
                  </el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="服务ID" prop="service_uuid" min-width="220" show-overflow-tooltip />
            <el-table-column label="状态" width="120">
              <template #default="scope">
                <div class="flex items-center">
                  <el-tag :type="getStatusType(scope.row)" size="small" class="mr-2">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                  <div v-if="isServiceOnline(scope.row)" class="online-indicator"></div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="SSE URL" min-width="240" show-overflow-tooltip>
              <template #default="scope">
                <div class="flex items-center">
                  <el-tooltip :content="scope.row.sse_url" placement="top" :show-after="500">
                    <el-input v-model="scope.row.sse_url" readonly size="small" class="flex-1 mr-1" disabled />
                  </el-tooltip>
                  <el-button type="primary" circle size="small" @click="copyUrl(scope.row.sse_url)" title="复制URL">
                    <el-icon>
                      <DocumentCopy />
                    </el-icon>
                  </el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="created_at" width="180" />
            <el-table-column label="操作" width="230" fixed="right">
              <template #default="scope">
                <div class="flex space-x-1">
                  <el-button v-if="scope.row.status !== 'running'" type="success" size="small"
                    :loading="loadingStates[scope.row.service_uuid]?.starting"
                    @click="startMcpService(scope.row.service_uuid)">
                    启动
                  </el-button>
                  <el-button v-else type="warning" size="small"
                    :loading="loadingStates[scope.row.service_uuid]?.stopping"
                    @click="stopMcpService(scope.row.service_uuid)">
                    停止
                  </el-button>

                  <el-button type="primary" size="small" @click="viewServiceDetail(scope.row)">
                    查看详情
                  </el-button>

                  <el-button type="danger" size="small" :loading="loadingStates[scope.row.service_uuid]?.deleting"
                    @click="confirmDeleteService(scope.row.service_uuid)">
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </el-main>

    <!-- 编辑服务说明对话框 -->
    <el-dialog v-model="dialogVisible" title="编辑服务说明" width="500px" :close-on-click-modal="false">
      <el-form :model="newDescription" label-position="top">
        <el-form-item label="服务说明">
          <el-input v-model="newDescription" type="textarea" :rows="4" placeholder="请输入服务说明" maxlength="500"
            show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveServiceDescription">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { DocumentCopy, Refresh, Edit } from '@element-plus/icons-vue';
import api from '../../api/index';
import { listServices, startService, stopService, getOnlineServices } from '@/api/marketplace';

// 定义服务类型接口
interface Service {
  service_uuid: string;
  name: string;
  description: string;
  status: string;
  version: string;
  created_at: string;
  updated_at: string;
  [key: string]: any; // 允许其他属性
}

// 定义日志类型接口
interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  [key: string]: any; // 允许其他属性
}

// 定义状态类型
interface StatusConfig {
  [key: string]: {
    label: string;
    type: string;
  }
}

// 定义加载状态接口
interface LoadingStates {
  [serviceUuid: string]: {
    [action: string]: boolean;
  };
}

const router = useRouter();
const services = ref<Service[]>([]);
const loading = ref(true);
const onlineServices = ref(new Set<string>());
const currentServiceLogs = ref<LogEntry[]>([]);
const logsLoading = ref(false);
const logsDialogVisible = ref(false);
const currentServiceName = ref('');

// 记录每个服务ID的加载状态
const loadingStates = reactive<LoadingStates>({});

// 状态映射配置
const statusConfig: StatusConfig = {
  'running': {
    label: '运行中',
    type: 'success'
  },
  'stopped': {
    label: '已停止',
    type: 'danger'
  },
  'error': {
    label: '错误',
    type: 'danger'
  },
  'starting': {
    label: '启动中',
    type: 'warning'
  },
  'stopping': {
    label: '停止中',
    type: 'warning'
  }
};

// 获取所有服务列表
const fetchServices = async () => {
  loading.value = true;
  try {
    const data = await listServices();
    console.log(data);
    services.value = data.data || [];

    // 获取在线服务状态
    await checkOnlineServices();
  } catch (error) {
    console.error('获取服务列表失败:', error);
    ElMessage.error('获取服务列表失败');
  } finally {
    loading.value = false;
  }
};

// 检查哪些服务在线
const checkOnlineServices = async () => {
  try {
    const data = await getOnlineServices();
    onlineServices.value = new Set(data.data);
  } catch (error) {
    console.error('获取在线服务状态失败', error);
  }
};

// 判断服务是否在线
const isServiceOnline = (service: Service) => {
  return onlineServices.value.has(service.service_uuid);
};

// 刷新服务列表
const refreshServices = async () => {
  await fetchServices();
  ElMessage.success('已刷新服务列表');
};

// 获取服务状态类型
const getStatusType = (service: Service) => {
  // 如果服务在线但状态不是running，优先显示在线状态
  if (isServiceOnline(service)) {
    return 'success';
  }

  switch (service.status) {
    case 'running': return 'success';
    case 'stopped': return 'warning';
    case 'error': return 'danger';
    default: return 'info';
  }
};

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'running': return '运行中';
    case 'stopped': return '已停止';
    case 'error': return '错误';
    default: return status;
  }
};

// 启动服务
const startMcpService = async (serviceUuid: string) => {
  if (!loadingStates[serviceUuid]) {
    loadingStates[serviceUuid] = {};
  }
  loadingStates[serviceUuid].starting = true;

  try {
    await startService(serviceUuid);
    ElMessage.success('服务已启动');
    await fetchServices();
  } catch (error) {
    console.error('启动服务失败', error);
    ElMessage.error('启动服务失败');
  } finally {
    loadingStates[serviceUuid].starting = false;
  }
};

// 停止服务
const stopMcpService = async (serviceUuid: string) => {
  if (!loadingStates[serviceUuid]) {
    loadingStates[serviceUuid] = {};
  }
  loadingStates[serviceUuid].stopping = true;

  try {
    await stopService(serviceUuid);
    ElMessage.success('服务已停止');
    await fetchServices();
  } catch (error) {
    console.error('停止服务失败', error);
    ElMessage.error('停止服务失败');
  } finally {
    loadingStates[serviceUuid].stopping = false;
  }
};

// 确认删除服务
const confirmDeleteService = (serviceUuid: string) => {
  ElMessageBox.confirm(
    '确定要删除此服务吗？删除后将无法恢复。',
    '确认删除',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      deleteService(serviceUuid);
    })
    .catch(() => {
      // 用户取消操作
    });
};

// 删除服务
const deleteService = async (serviceUuid: string) => {
  if (!loadingStates[serviceUuid]) {
    loadingStates[serviceUuid] = {};
  }
  loadingStates[serviceUuid].deleting = true;

  try {
    await api.post(`/api/services/${serviceUuid}/uninstall`);
    ElMessage.success('服务已删除');
    await fetchServices();
  } catch (error) {
    console.error('删除服务失败', error);
    ElMessage.error('删除服务失败');
  } finally {
    loadingStates[serviceUuid].deleting = false;
  }
};

// 查看服务详情
const viewServiceDetail = (service: Service) => {
  router.push(`/marketplace/${service.module_id}`);
};

// 复制URL到剪贴板
const copyUrl = (url: string) => {
  // 首先尝试使用现代的clipboard API
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url)
      .then(() => {
        ElMessage.success('URL已复制到剪贴板');
      })
      .catch(error => {
        // 如果clipboard API失败，使用传统方法
        fallbackCopyTextToClipboard(url);
      });
  } else {
    // 浏览器不支持clipboard API，使用传统方法
    fallbackCopyTextToClipboard(url);
  }
};

// 兼容性处理方法
const fallbackCopyTextToClipboard = (text: string) => {
  try {
    // 创建临时文本区域
    const textArea = document.createElement('textarea');
    textArea.value = text;

    // 确保文本区域在视图之外
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);

    // 选择文本
    textArea.select();
    textArea.setSelectionRange(0, 99999); // 兼容移动设备

    // 执行复制
    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);

    if (successful) {
      ElMessage.success('URL已复制到剪贴板');
    } else {
      ElMessage.warning('无法复制URL，请手动复制');
    }
  } catch (err) {
    ElMessage.error('复制失败，请手动复制URL');
    console.error('复制失败:', err);
  }
};

// 页面加载时获取服务列表
onMounted(() => {
  fetchServices();
});

// 编辑服务说明对话框
const dialogVisible = ref(false);
const editingService = ref<Service | null>(null);
const newDescription = ref('');

// 打开编辑服务说明对话框
const editServiceDescription = (service: Service) => {
  editingService.value = service;
  newDescription.value = service.description || '';
  dialogVisible.value = true;
};

// 保存服务说明
const saveServiceDescription = async () => {
  if (!editingService.value) return;

  try {
    await api.put(`/api/services/${editingService.value.service_uuid}/description`, {
      description: newDescription.value
    });

    // 更新本地数据
    editingService.value.description = newDescription.value;
    ElMessage.success('服务说明已更新');
    dialogVisible.value = false;
  } catch (error) {
    console.error('更新服务说明失败', error);
    ElMessage.error('更新服务说明失败');
  }
};

const copyServiceId = (service: Service) => {
  // ... existing code ...
};

const getStatusInfo = (service: Service) => {
  // ... existing code ...
};

const getStatusClass = (status: string) => {
  // ... existing code ...
};

const confirmUninstall = (serviceUuid: string) => {
  // ... existing code ...
};

const editService = (serviceUuid: string) => {
  // ... existing code ...
};

/**
 * 显示服务日志
 */
const showLogs = async (service: Service): Promise<void> => {
  currentServiceName.value = service.name || '';
  logsDialogVisible.value = true;
  logsLoading.value = true;

  try {
    const response = await api.get(`/mcp/service/${service.service_uuid}/logs`);
    currentServiceLogs.value = response.data?.data || [];
  } catch (error) {
    ElMessage.error('获取日志失败');
    console.error('获取日志错误:', error);
  } finally {
    logsLoading.value = false;
  }
};
</script>

<style scoped>
.online-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #67c23a;
  box-shadow: 0 0 5px 1px rgba(103, 194, 58, 0.5);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.5);
  }

  70% {
    box-shadow: 0 0 0 5px rgba(103, 194, 58, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
  }
}

:deep(.el-input__wrapper) {
  box-shadow: none;
  border: 1px solid #e0e3e9;
}

:deep(.el-input__inner) {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
  background-color: #f8f9fb;
}

.description-text {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>