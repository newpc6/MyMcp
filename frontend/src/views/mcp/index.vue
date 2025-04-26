<template>
  <div class="mcp-services-list">
    <div class="services-header">
      <h1 class="page-title">MCP服务</h1>
      <el-button type="primary" @click="loadServices" :loading="loading" class="refresh-button" round>
        <el-icon class="mr-1">
          <Refresh />
        </el-icon>
        刷新
      </el-button>
    </div>

    <el-row :gutter="24" v-loading="loading">
      <!-- 服务卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="6" v-for="service in services" :key="service.id"
        class="service-col">
        <el-card class="service-card" shadow="hover" :body-style="{ padding: '0px' }"
          :class="{ 'service-running': service.status === 'running' }">
          <div class="card-content">
            <div class="card-header">
              <div class="service-status">
                <span class="status-dot" :class="getStatusClass(service.status)"></span>
                <span class="status-text">{{ getStatusText(service.status) }}</span>
              </div>

              <!-- 右上角操作按钮 -->
              <div class="service-actions">
                <el-tooltip content="启动服务" v-if="service.status !== 'running'">
                  <el-button type="success" circle size="small" @click.stop="handleStartService(service)"
                    :disabled="!canManageService(service)" class="action-button">
                    <el-icon>
                      <VideoPlay />
                    </el-icon>
                  </el-button>
                </el-tooltip>

                <el-tooltip content="停止服务" v-if="service.status === 'running'">
                  <el-button type="warning" circle size="small" @click.stop="handleStopService(service)"
                    :disabled="!canManageService(service)" class="action-button">
                    <el-icon>
                      <VideoPause />
                    </el-icon>
                  </el-button>
                </el-tooltip>

                <el-tooltip content="删除服务">
                  <el-button type="danger" circle size="small" @click.stop="handleUninstallService(service)"
                    :disabled="!canManageService(service)" class="action-button">
                    <el-icon>
                      <Delete />
                    </el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </div>

            <div class="service-info">
              <h2 class="service-name">{{ service.module_name || '未命名服务' }}</h2>
              <p class="service-description">{{ service.description || '暂无描述' }}</p>
            </div>

            <div class="service-details">
              <div class="detail-item">
                <span class="detail-label">创建者</span>
                <span class="detail-value">{{ service.user_name || '未知' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">创建时间</span>
                <span class="detail-value">{{ formatDate(service.created_at) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">SSE URL</span>
                <div class="url-container">
                  <el-tooltip content="复制URL" placement="top">
                    <el-text class="url-text" type="primary" truncated @click.stop="copyToClipboard(service.sse_url)">
                      {{ service.sse_url }}
                    </el-text>
                  </el-tooltip>
                  <el-button link type="primary" @click.stop="copyToClipboard(service.sse_url)" class="copy-button">
                    <el-icon>
                      <CopyDocument />
                    </el-icon>
                  </el-button>
                </div>
                <el-text v-if="service.status === 'error'" type="danger" size="small" truncated>
                  {{ service.error_message }}
                </el-text>
              </div>
            </div>

            <div class="service-footer" v-if="!canManageService(service)">
              <el-tag type="warning" size="small" effect="plain">无操作权限</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 添加新服务卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="6" class="service-col">
        <el-card class="add-service-card" shadow="hover" @click="goToCreateService">
          <div class="add-service-content">
            <el-icon class="add-icon">
              <Plus />
            </el-icon>
            <span class="add-text">创建新服务</span>
          </div>
        </el-card>
      </el-col>

      <!-- 空状态显示 -->
      <el-col :span="24" v-if="services.length === 0 && !loading">
        <div class="empty-container">
          <el-empty description="暂无发布的MCP服务">
            <el-button type="primary" @click="loadServices" round>刷新</el-button>
            <el-button type="success" @click="goToCreateService" round>创建服务</el-button>
          </el-empty>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus';
import { VideoPlay, VideoPause, Delete, Refresh, CopyDocument, Plus } from '@element-plus/icons-vue';
import {
  listServices,
  startService,
  stopService,
  uninstallService
} from '../../api/marketplace';
import { fallbackCopyTextToClipboard } from '../../utils/copy';
import type { McpServiceInfo } from '../../types/marketplace';

// 路由
const router = useRouter();

// 加载状态
const loading = ref(false);
// 服务列表
const services = ref<McpServiceInfo[]>([]);

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
const canManageService = (service: McpServiceInfo) => {
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

// 前往创建服务页面
const goToCreateService = () => {
  router.push('/marketplace');
};

// 启动服务
const handleStartService = async (service: McpServiceInfo) => {
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
const handleStopService = async (service: McpServiceInfo) => {
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
const handleUninstallService = async (service: McpServiceInfo) => {
  // 阻止事件冒泡
  event?.stopPropagation();

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
      `确认要卸载服务 ${service.module_name || '未命名服务'} 吗？此操作不可恢复！`,
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
const copyToClipboard = (url: string) => {
  // 阻止事件冒泡
  event?.stopPropagation();

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

// 获取服务状态样式类名
const getStatusClass = (status: string) => {
  switch (status) {
    case 'running':
      return 'status-running';
    case 'stopped':
      return 'status-stopped';
    case 'error':
      return 'status-error';
    default:
      return 'status-unknown';
  }
};

// 获取服务状态文字
const getStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中';
    case 'stopped':
      return '已停止';
    case 'error':
      return '错误';
    default:
      return '未知';
  }
};

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '未知';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 截断URL显示
const truncateUrl = (url: string) => {
  if (!url) return '';
  return url.length > 30 ? url.substring(0, 30) + '...' : url;
};

// 页面加载时获取服务列表
onMounted(() => {
  loadUserInfo();
  loadServices();
});
</script>

<style scoped>
.mcp-services-list {
  padding: 24px;
  max-width: 1440px;
  margin: 0 auto;
}

.services-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.refresh-button {
  border-radius: 20px;
  padding: 8px 20px;
  font-weight: 500;
}

.service-col {
  margin-bottom: 24px;
}

.service-card {
  height: 100%;
  border-radius: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.service-running {
  border-left: 4px solid #67c23a;
}

.card-content {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.service-status {
  display: flex;
  align-items: center;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  position: relative;
}

.status-running {
  background-color: #67c23a;
  box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.2);
}

.status-running::after {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border-radius: 50%;
  background-color: rgba(103, 194, 58, 0.2);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }

  70% {
    transform: scale(1.5);
    opacity: 0;
  }

  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.status-stopped {
  background-color: #909399;
  box-shadow: 0 0 0 3px rgba(144, 147, 153, 0.2);
}

.status-error {
  background-color: #f56c6c;
  box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.2);
}

.status-unknown {
  background-color: #e6a23c;
  box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.2);
}

.status-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.service-actions {
  display: flex;
  gap: 8px;
}

.action-button {
  font-size: 12px;
}

.service-info {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.service-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
}

.service-description {
  font-size: 14px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
  max-height: 66px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.service-details {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: #303133;
}

.url-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f5f7fa;
  border-radius: 6px;
  padding: 6px 10px;
}

.url-text {
  font-size: 13px;
  cursor: pointer;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.copy-button {
  padding: 2px;
}

.service-footer {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.empty-container {
  padding: 80px 0;
  text-align: center;
}

.add-service-card {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 16px;
  border: 2px dashed #dcdfe6;
  background-color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s;
}

.add-service-card:hover {
  transform: translateY(-4px);
  border-color: #409eff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.add-service-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
}

.add-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 16px;
}

.add-text {
  font-size: 16px;
  color: #409eff;
  font-weight: 500;
}

/* 适配暗色主题 */
:root[data-theme="dark"] .service-card {
  background-color: rgba(48, 49, 51, 0.8);
  border-color: #484848;
}

:root[data-theme="dark"] .add-service-card {
  background-color: rgba(48, 49, 51, 0.5);
  border-color: #606266;
}

:root[data-theme="dark"] .add-service-card:hover {
  border-color: #409eff;
}

:root[data-theme="dark"] .url-container {
  background-color: rgba(0, 0, 0, 0.2);
}
</style>