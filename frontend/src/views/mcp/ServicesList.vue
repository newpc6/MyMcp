<template>
  <div class="mcp-services-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2 class="text-xl">已发布的MCP服务</h2>
          <el-button type="primary" @click="loadServices" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-table 
        :data="services" 
        stripe 
        border 
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column 
          label="ID"
          prop="id"
          width="80"
        ></el-table-column>
        
        <el-table-column 
          label="模块名称"
          prop="module_name"
          width="150"
        ></el-table-column>
        
        <el-table-column 
          label="描述"
          prop="description"
          width="200"
        ></el-table-column>
        
        <el-table-column 
          label="创建者"
          prop="user_name"
          width="100"
        ></el-table-column>
        
        <el-table-column 
          label="状态"
          prop="status"
          width="120"
        >
          <template #default="scope">
            <el-tag :type="getStatusClass(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column 
          label="SSE URL"
          prop="sse_url"
          width="300"
        >
          <template #default="scope">
            <div class="flex items-center">
              <el-tooltip content="复制URL">
                <el-button 
                  link 
                  type="primary" 
                  @click="copyToClipboard(scope.row.sse_url)"
                >
                  <span class="truncate block" style="max-width: 280px;">
                    {{ scope.row.sse_url }}
                  </span>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column 
          label="创建时间"
          prop="created_at"
          width="180"
        ></el-table-column>
        
        <el-table-column 
          label="操作"
          width="200"
          fixed="right"
        >
          <template #default="scope">
            <div class="button-group">
              <el-tooltip content="启动服务" v-if="scope.row.status !== 'running'">
                <el-button 
                  type="success" 
                  size="small" 
                  circle
                  @click="handleStartService(scope.row)"
                  :disabled="!canManageService(scope.row)"
                >
                  <el-icon><VideoPlay /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="停止服务" v-if="scope.row.status === 'running'">
                <el-button 
                  type="warning" 
                  size="small" 
                  circle
                  @click="handleStopService(scope.row)"
                  :disabled="!canManageService(scope.row)"
                >
                  <el-icon><VideoPause /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="删除服务">
                <el-button 
                  type="danger" 
                  size="small" 
                  circle
                  @click="handleUninstallService(scope.row)"
                  :disabled="!canManageService(scope.row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip :content="canManageService(scope.row) ? '' : '您没有权限操作此服务'" v-if="!canManageService(scope.row)">
                <el-tag type="warning" size="small" class="ml-2">
                  无权限
                </el-tag>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="services.length === 0 && !loading" class="empty-container">
        <el-empty description="暂无发布的MCP服务">
          <el-button type="primary" @click="loadServices">刷新</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus';
import { VideoPlay, VideoPause, Delete } from '@element-plus/icons-vue';
import { 
  listServices, 
  startService, 
  stopService, 
  uninstallService 
} from '../../api/marketplace';

// 服务类型接口
interface McpService {
  id: number;
  module_id: number;
  module_name: string;
  description: string;
  service_uuid: string;
  status: string;
  sse_url: string;
  user_id?: number | null;
  user_name?: string | null;
  created_at: string;
  updated_at: string;
}

// 加载状态
const loading = ref(false);
// 服务列表
const services = ref<McpService[]>([]);

// 用户信息
const currentUser = ref<{
  user_id: number | null;
  username: string;
  is_admin: boolean;
}>({
  user_id: null,
  username: '',
  is_admin: false
});

// 加载用户信息
const loadUserInfo = () => {
  try {
    const userInfoStr = localStorage.getItem('userInfo');
    if (userInfoStr) {
      const userInfo = JSON.parse(userInfoStr);
      currentUser.value = {
        user_id: userInfo.user_id || null,
        username: userInfo.username || '',
        is_admin: userInfo.is_admin || false
      };
    }
  } catch (error) {
    console.error('获取用户信息失败', error);
  }
};

// 检查是否有权限操作服务
const canManageService = (service: McpService) => {
  // 如果是管理员，可以操作所有服务
  if (currentUser.value.is_admin) {
    return true;
  }
  
  // 否则只能操作自己创建的服务
  return service.user_id === currentUser.value.user_id;
};

// 加载服务列表
const loadServices = async () => {
  loading.value = true;
  try {
    const response = await listServices();
    if (response && response.data) {
      services.value = response.data;
    } else {
      services.value = [];
    }
  } catch (error: any) {
    ElMessage.error(`获取服务列表失败: ${error.message || '未知错误'}`);
  } finally {
    loading.value = false;
  }
};

// 启动服务
const handleStartService = async (service: McpService) => {
  // 检查权限
  if (!canManageService(service)) {
    ElMessageBox.alert(
      '您没有权限操作此服务，只有管理员或服务创建者才能操作。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  try {
    const response = await startService(service.service_uuid);
    ElNotification({
      title: '成功',
      message: '服务已启动',
      type: 'success'
    });
    loadServices();
  } catch (error: any) {
    ElNotification({
      title: '错误',
      message: `启动服务失败: ${error.message || '未知错误'}`,
      type: 'error'
    });
  }
};

// 停止服务
const handleStopService = async (service: McpService) => {
  // 检查权限
  if (!canManageService(service)) {
    ElMessageBox.alert(
      '您没有权限操作此服务，只有管理员或服务创建者才能操作。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  try {
    const response = await stopService(service.service_uuid);
    ElNotification({
      title: '成功',
      message: '服务已停止',
      type: 'success'
    });
    loadServices();
  } catch (error: any) {
    ElNotification({
      title: '错误',
      message: `停止服务失败: ${error.message || '未知错误'}`,
      type: 'error'
    });
  }
};

// 删除服务
const handleUninstallService = async (service: McpService) => {
  // 检查权限
  if (!canManageService(service)) {
    ElMessageBox.alert(
      '您没有权限操作此服务，只有管理员或服务创建者才能操作。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确认要卸载服务 ${service.module_name} 吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    const response = await uninstallService(service.service_uuid);
    ElNotification({
      title: '成功',
      message: '服务已成功卸载',
      type: 'success'
    });
    loadServices();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElNotification({
        title: '错误',
        message: `卸载服务失败: ${error.message || '未知错误'}`,
        type: 'error'
      });
    }
  }
};

// 复制URL到剪贴板
const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
    .then(() => {
      ElMessage.success('已复制到剪贴板');
    })
    .catch(err => {
      ElMessage.error('复制失败');
      console.error('复制失败:', err);
    });
};

// 获取服务状态样式
const getStatusClass = (status: string) => {
  switch (status) {
    case 'running':
      return 'success';
    case 'stopped':
      return 'info';
    case 'error':
      return 'danger';
    default:
      return 'warning';
  }
};

// 页面加载时获取服务列表
onMounted(() => {
  loadUserInfo();
  loadServices();
});
</script>

<style scoped>
.mcp-services-list {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.button-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-container {
  padding: 40px 0;
  text-align: center;
}
</style>