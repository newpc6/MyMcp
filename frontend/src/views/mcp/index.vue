<template>
  <div class="mcp-services-list">
    <div class="services-header">
      <h1 class="page-title">MCP服务</h1>
      <div class="header-actions">
        <!-- 搜索表单 -->
        <div class="search-form">
          <el-input v-model="pageQuery.condition.name" placeholder="搜索服务名称" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 200px; margin-right: 10px;" />
          <el-select v-model="pageQuery.condition.module_id" placeholder="搜索MCP模板" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 200px; margin-right: 10px;" @change="handleSearch">
            <el-option v-for="(module, index) in modules" :key="index" :label="module.name" :value="module.id">
              <span style="float: left">{{ index + 1 }}. {{ module.name }}</span>
            </el-option>
          </el-select>
          <el-select v-model="pageQuery.condition.status" placeholder="选择状态" clearable @clear="handleSearch"
            @change="handleSearch" style="width: 120px; margin-right: 10px;">
            <el-option label="运行中" value="running" />
            <el-option label="已停止" value="stopped" />
            <el-option label="错误" value="error" />
          </el-select>
          <el-select v-model="pageQuery.condition.user_id" placeholder="搜索创建者" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 150px; margin-right: 10px;" @change="handleSearch">
            <el-option v-for="user in users" :key="user.id" :label="user.username" :value="user.id">
              <span style="float: left">{{ user.username }}</span>
              <el-icon v-if="user.is_admin" class="mr-1">
                <UserFilled />
              </el-icon>
            </el-option>
          </el-select>
          <el-button type="primary" @click="handleSearch" round>
            <el-icon class="mr-1">
              <Search />
            </el-icon>
            搜索
          </el-button>
        </div>
        <el-button type="primary" @click="loadServices" :loading="loading" class="refresh-button" round>
          <el-icon class="mr-1">
            <Refresh />
          </el-icon>
          刷新
        </el-button>
      </div>
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
                <!-- 公开状态标签 -->
                <div class="public-status">
                  <el-tag v-if="service.is_public" type="success" size="small" class="public-tag">
                    公开
                  </el-tag>
                  <el-tag v-else type="info" size="small" class="public-tag">
                    私有
                  </el-tag>
                </div>
              </div>

              <!-- 权限状态和操作按钮 -->
              <div class="service-actions">
                <!-- 无权限时显示锁图标 -->
                <el-tooltip content="无管理权限，仅可使用" v-if="!canManageService(service)">
                  <el-icon class="lock-icon" size="16">
                    <Lock />
                  </el-icon>
                </el-tooltip>

                <!-- 有权限时显示管理按钮 -->
                <template v-else>
                  <el-tooltip content="参数管理" v-if="hasConfigParams(service)">
                    <el-button type="info" circle size="small" @click.stop="handleViewServiceParams(service)"
                      class="action-button">
                      <el-icon>
                        <Setting />
                      </el-icon>
                    </el-button>
                  </el-tooltip>

                  <el-tooltip content="启动服务" v-if="service.status !== 'running'">
                    <el-button type="success" circle size="small" @click.stop="handleStartService(service)"
                      class="action-button">
                      <el-icon>
                        <VideoPlay />
                      </el-icon>
                    </el-button>
                  </el-tooltip>

                  <el-tooltip content="停止服务" v-if="service.status === 'running'">
                    <el-button type="warning" circle size="small" @click.stop="handleStopService(service)"
                      class="action-button">
                      <el-icon>
                        <VideoPause />
                      </el-icon>
                    </el-button>
                  </el-tooltip>

                  <el-tooltip content="删除服务">
                    <el-button type="danger" circle size="small" @click.stop="handleUninstallService(service)"
                      class="action-button">
                      <el-icon>
                        <Delete />
                      </el-icon>
                    </el-button>
                  </el-tooltip>
                </template>
              </div>
            </div>

            <div class="service-info">
              <!-- 模板和名称放一行 -->
              <div class="service-title-row">
                <div class="service-title-item">
                  <span class="title-label">名称：</span>
                  <el-text truncated class="title-value">{{ service.name || '默认' }}</el-text>
                </div>
                <div class="service-title-item">
                  <span class="title-label">模板：</span>
                  <el-text truncated class="title-value">{{ service.module_name || '未命名服务' }}</el-text>
                </div>
              </div>

              <!-- 描述 -->
              <div class="service-description">
                <el-text truncated type="info" size="small">
                  {{ service.description || '暂无描述' }}
                </el-text>
              </div>
            </div>

            <div class="service-details">
              <!-- 创建者和创建时间放一行 -->
              <div class="detail-row">
                <div class="detail-item">
                  <span class="detail-label">创建者</span>
                  <span class="detail-value">{{ service.user_name || '未知' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">创建时间</span>
                  <span class="detail-value">{{ formatDate(service.created_at) }}</span>
                </div>
              </div>

              <!-- SSE URL -->
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
                  <el-tooltip content="复制为egovakb格式" placement="top">
                    <el-button link type="success" @click.stop="copyAsEgovakbUrl(service.sse_url)" class="copy-button">
                      <el-icon>
                        <Connection />
                      </el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
                <el-text v-if="service.status === 'error'" type="danger" size="small" truncated>
                  {{ service.error_message }}
                </el-text>
              </div>
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

    <!-- 分页组件 -->
    <div v-if="!loading && total > 0" class="pagination-container">
      <el-config-provider :locale="zhCn">
        <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[7, 11, 15, 19]"
        :background="true" layout="total, sizes, prev, pager, next, jumper" :total="total"
        @size-change="handleSizeChange" @current-change="handleCurrentChange" />
      </el-config-provider>
    </div>

    <!-- 服务参数管理对话框 -->
    <el-dialog v-model="serviceParamsDialogVisible" title="服务参数管理" width="50%" :destroy-on-close="true">
      <ServiceParamsManager v-if="currentService && currentServiceSchema" :config-params="serviceParamsForm"
        :config-schema="currentServiceSchema" @update:config-params="updateServiceParamsForm"
        ref="serviceParamsManagerRef" />
      <div v-else class="text-center py-4">
        <el-empty description="无法加载服务参数" :image-size="60" />
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="serviceParamsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateServiceParams" :loading="updatingParams">更新参数</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { VideoPlay, VideoPause, Delete, Refresh, CopyDocument, Plus, Connection, Lock, Setting, Search } from '@element-plus/icons-vue';
import {
  listServices,
  startService,
  stopService,
  uninstallService,
  getService,
  getModule,
  pageServices,
  listModules
} from '../../api/marketplace';
import { updateServiceParams as updateServiceParamsAPI } from '../../api/mcpServer';
import { fallbackCopyTextToClipboard, copyTextToClipboard } from '../../utils/copy';
import type { McpServiceInfo } from '../../types/marketplace';
// @ts-ignore
import ServiceParamsManager from '../../components/ServiceParamsManager.vue';
import { Page } from '../../types/page';
import { getAllUsers } from '@/api/auth';

// 路由
const router = useRouter();

// 加载状态
const loading = ref(false);
// 服务列表
const services = ref<McpServiceInfo[]>([]);

// 分页相关状态
const currentPage = ref(1);
const pageSize = ref(7);
const total = ref(0);

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

// 参数管理相关
const serviceParamsDialogVisible = ref(false);
const currentService = ref<McpServiceInfo | null>(null);
const currentServiceSchema = ref<Record<string, any> | null>(null);
const serviceParamsForm = ref<Record<string, any>>({});
const serviceParamsManagerRef = ref();
const updatingParams = ref(false);

// 构建查询参数
const pageQuery = reactive<Page>({
  paging: {
    page: currentPage.value,
    size: pageSize.value,
  },
  condition: {
    name: "",
    module_id: null,
    status: "",
    user_id: null
  }
});

// 模块和用户数据用于下拉选择
const modules = ref<{ id: number, name: string, description: string }[]>([]);
const users = ref<{ id: number, username: string, is_admin: boolean }[]>([]);

// 加载模块数据
const loadModules = async () => {
  try {
    const data = await listModules();
    if (data ) {
      modules.value = data.data;
    }
  } catch (error) {
    console.error('获取模块列表失败', error);
  }
};

// 加载用户数据
const loadUsers = async () => {
  try {
    const response = await getAllUsers();
    if (response && response.data) {
      users.value = response.data;
    }
  } catch (error: any) {
    // 非管理员可能没有权限查看用户列表，这是正常的
    console.log('获取用户列表失败（可能无权限）', error.message);
  }
};

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
  // 优先使用后端返回的can_edit字段
  if (service.can_edit !== undefined) {
    return service.can_edit;
  }

  // 如果没有can_edit字段，使用原有逻辑作为兜底
  // 如果是管理员，可以操作所有服务
  if (currentUser.value.is_admin) {
    return true;
  }

  // 否则只能操作自己创建的服务
  return service.user_id === currentUser.value.user_id;
};

// 加载服务列表
const loadServices = async () => {
  console.log('loadServices');
  loading.value = true;
  try {
    // 同步当前分页信息到查询参数
    pageQuery.paging.page = currentPage.value;
    pageQuery.paging.size = pageSize.value;

    const response = await pageServices(pageQuery);
    if (response && response.data) {
      services.value = response.data.items || [];
      total.value = response.data.total || 0;
      currentPage.value = response.data.page || 1;
      pageSize.value = response.data.size || 10;
    } else {
      services.value = [];
      total.value = 0;
    }
  } catch (error: any) {
    ElMessage.error(`获取服务列表失败: ${error.message || '未知错误'}`);
    services.value = [];
    total.value = 0;
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

  copyTextToClipboard(url, 'URL已复制到剪贴板');
};

// 复制为egovakb格式的URL
const copyAsEgovakbUrl = (url: string) => {
  // 阻止事件冒泡
  event?.stopPropagation();

  // 创建egovakb格式的JSON
  const egovakbFormat = JSON.stringify({
    "在线搜索": {
      "url": url,
      "transport": "sse"
    }
  }, null, 2);

  // 复制到剪贴板
  copyTextToClipboard(egovakbFormat, 'egovakb格式URL已复制到剪贴板');
};

// 检查服务是否有配置参数
const hasConfigParams = (service: McpServiceInfo) => {
  return service.config_params && Object.keys(service.config_params).length > 0;
};

// 查看服务参数
const handleViewServiceParams = async (service: McpServiceInfo) => {
  try {
    // 获取最新的服务信息
    const serviceResponse = await getService(service.service_uuid);
    if (serviceResponse && serviceResponse.data) {
      currentService.value = serviceResponse.data;
      // 初始化表单
      serviceParamsForm.value = { ...serviceResponse.data.config_params };

      // 获取模块的配置schema
      const moduleResponse = await getModule(serviceResponse.data.module_id);
      if (moduleResponse && moduleResponse.data && moduleResponse.data.config_schema) {
        currentServiceSchema.value = moduleResponse.data.config_schema;
      } else {
        currentServiceSchema.value = null;
      }

      serviceParamsDialogVisible.value = true;
    }
  } catch (error) {
    console.error('获取服务参数失败', error);
    ElMessage.error('获取服务参数失败');
  }
};

// 更新服务参数表单
const updateServiceParamsForm = (newParams: Record<string, any>) => {
  serviceParamsForm.value = { ...newParams };
};

// 更新服务参数
const updateServiceParams = async () => {
  if (!currentService.value) return;

  updatingParams.value = true;
  try {
    // 调用API更新服务参数
    await updateServiceParamsAPI(currentService.value.id, serviceParamsForm.value);
    ElMessage.success('服务参数更新成功');
    serviceParamsDialogVisible.value = false;

    // 重新加载服务列表
    await loadServices();
  } catch (error) {
    console.error('更新服务参数失败', error);
    ElMessage.error('更新服务参数失败');
  } finally {
    updatingParams.value = false;
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

// 处理分页大小变化
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize;
  currentPage.value = 1; // 重置到第一页
  loadServices();
};

// 处理当前页变化
const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage;
  loadServices();
};

// 搜索服务
const handleSearch = async () => {
  currentPage.value = 1; // 重置到第一页
  await loadServices();
};

// 页面加载时获取服务列表
onMounted(() => {
  loadUserInfo();
  loadModules();
  loadUsers();
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
  flex-wrap: wrap;
  gap: 16px;
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
  /* transition: all 0.3s ease; */
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.service-card:hover {
  /* transform: translateY(-4px); */
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
  margin-bottom: 12px;
}

.service-status {
  display: flex;
  align-items: center;
}

.public-status {
  margin-left: auto;
  margin-right: 8px;
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

.lock-icon {
  color: #909399;
  cursor: help;
}

.service-info {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.service-title-row {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.service-title-item {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.title-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  white-space: nowrap;
}

.title-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.service-description {
  margin-bottom: 0;
}

.service-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
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
  /* transition: all 0.3s; */
}

.add-service-card:hover {
  /* transform: translateY(-4px); */
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 20px 0;
}
</style>