<template>
  <div class="mcp-services-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon">
              <Promotion />
            </el-icon>
            MCP服务管理
          </h1>
          <!-- <p class="page-subtitle">管理和监控您的MCP服务实例</p> -->
        </div>
        
        <!-- 搜索和操作区域 -->
        <div class="header-actions">
          <div class="search-section">
            <el-input 
              v-model="pageQuery.condition.name" 
              placeholder="搜索服务名称" 
              clearable 
              @clear="handleSearch"
              @keyup.enter="handleSearch" 
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-select 
              v-model="pageQuery.condition.module_id" 
              placeholder="选择模板" 
              clearable 
              @clear="handleSearch"
              @change="handleSearch" 
              class="filter-select"
            >
              <el-option 
                v-for="(module, index) in modules" 
                :key="index" 
                :label="module.name" 
                :value="module.id"
              >
                <span class="option-text">{{ module.name }}</span>
              </el-option>
            </el-select>
            
            <el-select 
              v-model="pageQuery.condition.status" 
              placeholder="选择状态" 
              clearable 
              @clear="handleSearch"
              @change="handleSearch" 
              class="filter-select"
            >
              <el-option label="运行中" value="running" />
              <el-option label="已停止" value="stopped" />
              <el-option label="错误" value="error" />
            </el-select>
            
            <el-select 
              v-model="pageQuery.condition.user_id" 
              placeholder="选择创建者" 
              clearable 
              @clear="handleSearch"
              @change="handleSearch" 
              class="filter-select"
            >
              <el-option 
                v-for="user in users" 
                :key="user.id" 
                :label="user.username" 
                :value="user.id"
              >
                <span class="option-text">{{ user.username }}</span>
                <el-icon v-if="user.is_admin" class="admin-icon">
                  <UserFilled />
                </el-icon>
              </el-option>
            </el-select>
          </div>
          
          <div class="action-buttons">
            <el-button 
              type="primary" 
              @click="handleSearch" 
              class="search-btn"
            >
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            
            <el-button 
              type="default" 
              @click="loadServices" 
              :loading="loading" 
              class="refresh-btn"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 服务卡片网格 -->
    <div class="services-grid" v-loading="loading">
      <!-- 服务卡片 -->
      <div 
        v-for="service in services" 
        :key="service.id"
        class="service-card"
        :class="{ 'service-running': service.status === 'running' }"
      >
        <div class="card-header">
          <div class="status-section">
            <div class="status-indicator" :class="getStatusClass(service.status)">
              <span class="status-dot"></span>
              <span class="status-text">{{ getStatusText(service.status) }}</span>
            </div>
            
            <div class="visibility-badge">
              <el-tag 
                :type="service.is_public ? 'success' : 'info'" 
                size="small" 
                effect="light"
              >
                {{ service.is_public ? '公开' : '私有' }}
              </el-tag>
            </div>
          </div>

          <div class="action-section">
            <!-- 无权限时显示锁图标 -->
            <el-tooltip content="无管理权限，仅可使用" v-if="!canManageService(service)">
              <el-icon class="lock-icon">
                <Lock />
              </el-icon>
            </el-tooltip>

            <!-- 有权限时显示管理按钮 -->
            <div v-else class="action-buttons">
              <el-tooltip content="参数管理" v-if="hasConfigParams(service)">
                <el-button 
                  type="info" 
                  circle 
                  size="small" 
                  @click.stop="handleViewServiceParams(service)"
                  class="action-btn"
                >
                  <el-icon><Setting /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="启动服务" v-if="service.status !== 'running'">
                <el-button 
                  type="success" 
                  circle 
                  size="small" 
                  @click.stop="handleStartService(service)"
                  class="action-btn"
                >
                  <el-icon><VideoPlay /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="停止服务" v-if="service.status === 'running'">
                <el-button 
                  type="warning" 
                  circle 
                  size="small" 
                  @click.stop="handleStopService(service)"
                  class="action-btn"
                >
                  <el-icon><VideoPause /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="删除服务">
                <el-button 
                  type="danger" 
                  circle 
                  size="small" 
                  @click.stop="handleUninstallService(service)"
                  class="action-btn"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </div>

        <div class="card-content">
          <div class="service-info">
            <h3 class="service-name">{{ service.name || '默认服务' }}</h3>
            <p class="service-module">{{ service.module_name || '未命名模块' }}</p>
            <p class="service-description">{{ service.description || '暂无描述' }}</p>
          </div>

          <div class="service-meta">
            <div class="meta-row">
              <div class="meta-item">
                <span class="meta-label">创建者</span>
                <span class="meta-value">{{ service.user_name || '未知' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">创建时间</span>
                <span class="meta-value">{{ formatDate(service.created_at) }}</span>
              </div>
            </div>

            <div class="url-section">
              <div class="url-label">SSE URL</div>
              <div class="url-container">
                <el-tooltip content="点击复制URL" placement="top">
                  <div class="url-text" @click.stop="copyToClipboard(service.sse_url)">
                    {{ service.sse_url }}
                  </div>
                </el-tooltip>
                <div class="url-actions">
                  <el-tooltip content="复制URL" placement="top">
                    <el-button 
                      link 
                      type="primary" 
                      @click.stop="copyToClipboard(service.sse_url)" 
                      class="url-btn"
                    >
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="复制为egovakb格式" placement="top">
                    <el-button 
                      link 
                      type="success" 
                      @click.stop="copyAsEgovakbUrl(service.sse_url)" 
                      class="url-btn"
                    >
                      <el-icon><Connection /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
              
              <div v-if="service.status === 'error'" class="error-message">
                <el-text type="danger" size="small">
                  {{ service.error_message }}
                </el-text>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加新服务卡片 -->
      <div class="add-service-card" @click="goToCreateService">
        <div class="add-content">
          <el-icon class="add-icon">
            <Plus />
          </el-icon>
          <span class="add-text">创建新服务</span>
          <span class="add-subtitle">点击开始创建MCP服务</span>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="services.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无MCP服务" :image-size="120">
          <template #description>
            <p class="empty-description">还没有创建任何MCP服务</p>
            <p class="empty-hint">点击下方按钮开始创建您的第一个服务</p>
          </template>
          <div class="empty-actions">
            <el-button type="primary" @click="goToCreateService" size="large">
              <el-icon><Plus /></el-icon>
              创建服务
            </el-button>
            <el-button @click="loadServices" size="large">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </el-empty>
      </div>
    </div>

    <!-- 分页组件 -->
    <div v-if="!loading && total > 0" class="pagination-wrapper">
      <el-config-provider :locale="zhCn">
        <el-pagination 
          :current-page="currentPage" 
          :page-size="pageSize" 
          :page-sizes="[7, 11, 15, 19]"
          :background="true" 
          layout="total, sizes, prev, pager, next, jumper" 
          :total="total"
          @size-change="handleSizeChange" 
          @current-change="handleCurrentChange"
          class="pagination"
        />
      </el-config-provider>
    </div>

    <!-- 服务参数管理对话框 -->
    <el-dialog 
      v-model="serviceParamsDialogVisible" 
      title="服务参数管理" 
      width="50%" 
      :destroy-on-close="true"
      class="params-dialog"
    >
      <ServiceParamsManager 
        v-if="currentService && currentServiceSchema" 
        :config-params="serviceParamsForm"
        :config-schema="currentServiceSchema" 
        @update:config-params="updateServiceParamsForm"
        ref="serviceParamsManagerRef" 
      />
      <div v-else class="dialog-empty">
        <el-empty description="无法加载服务参数" :image-size="60" />
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="serviceParamsDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="updateServiceParams" 
            :loading="updatingParams"
          >
            更新参数
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { 
  VideoPlay, 
  VideoPause, 
  Delete, 
  Refresh, 
  CopyDocument, 
  Plus, 
  Connection, 
  Lock, 
  Setting, 
  Search,
  Promotion,
  UserFilled
} from '@element-plus/icons-vue';
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
import { getAllUsers } from '../../api/auth';

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
.mcp-services-container {
  padding: 24px;
  /* max-width: 1440px; */
  margin: 0 auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 32px;
  flex-wrap: wrap;
}

.title-section {
  flex: 1;
  min-width: 300px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-icon {
  font-size: 28px;
  color: #667eea;
}

.page-subtitle {
  font-size: 16px;
  color: #718096;
  margin: 0;
  font-weight: 400;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 600px;
  flex-wrap: wrap;
}

.search-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  flex: 1;
}

.search-input {
  width: 220px;
}

.filter-select {
  width: 180px;
}

.option-text {
  font-weight: 500;
}

.admin-icon {
  color: #f56565;
  margin-left: 8px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-btn,
.refresh-btn {
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.search-btn:hover,
.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.service-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.service-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.service-running {
  border-left: 4px solid #48bb78;
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.1) 0%, rgba(255, 255, 255, 0.95) 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.status-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-running {
  background: rgba(72, 187, 120, 0.1);
  color: #38a169;
}

.status-running .status-dot {
  background: #48bb78;
  box-shadow: 0 0 0 3px rgba(72, 187, 120, 0.3);
  animation: pulse 2s infinite;
}

.status-stopped {
  background: rgba(160, 174, 192, 0.1);
  color: #718096;
}

.status-stopped .status-dot {
  background: #a0aec0;
}

.status-error {
  background: rgba(245, 101, 101, 0.1);
  color: #e53e3e;
}

.status-error .status-dot {
  background: #f56565;
}

.status-unknown {
  background: rgba(237, 137, 54, 0.1);
  color: #dd6b20;
}

.status-unknown .status-dot {
  background: #ed8936;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 3px rgba(72, 187, 120, 0.3);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(72, 187, 120, 0);
  }
  100% {
    box-shadow: 0 0 0 3px rgba(72, 187, 120, 0);
  }
}

.visibility-badge {
  margin-left: auto;
}

.action-section {
  display: flex;
  gap: 8px;
}

.action-buttons {
  display: flex;
  gap: 6px;
}

.action-btn {
  font-size: 12px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: scale(1.1);
}

.lock-icon {
  color: #a0aec0;
  cursor: help;
  font-size: 18px;
}

.card-content {
  padding: 24px;
}

.service-info {
  margin-bottom: 20px;
}

.service-name {
  font-size: 20px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.service-module {
  font-size: 14px;
  color: #667eea;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.service-description {
  font-size: 14px;
  color: #718096;
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.service-meta {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.meta-row {
  display: flex;
  gap: 20px;
}

.meta-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 12px;
  color: #a0aec0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-value {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.url-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.url-label {
  font-size: 12px;
  color: #a0aec0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.url-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 12px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.url-container:hover {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.url-text {
  font-size: 13px;
  cursor: pointer;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #4a5568;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  transition: color 0.2s ease;
}

.url-text:hover {
  color: #667eea;
}

.url-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 12px;
}

.url-btn {
  padding: 4px;
  transition: all 0.2s ease;
}

.url-btn:hover {
  transform: scale(1.1);
}

.error-message {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(245, 101, 101, 0.1);
  border-radius: 8px;
  border-left: 3px solid #f56565;
}

.add-service-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(255, 255, 255, 0.95) 100%);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 2px dashed #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  position: relative;
  overflow: hidden;
}

.add-service-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.add-service-card:hover::before {
  left: 100%;
}

.add-service-card:hover {
  transform: translateY(-8px);
  border-color: #5a67d8;
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
}

.add-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  z-index: 1;
}

.add-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.add-service-card:hover .add-icon {
  transform: scale(1.1);
  color: #5a67d8;
}

.add-text {
  font-size: 18px;
  color: #667eea;
  font-weight: 700;
  margin-bottom: 8px;
}

.add-subtitle {
  font-size: 14px;
  color: #718096;
  text-align: center;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 80px 20px;
  text-align: center;
}

.empty-description {
  font-size: 18px;
  color: #4a5568;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.empty-hint {
  font-size: 14px;
  color: #718096;
  margin: 0 0 24px 0;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding: 24px 0;
}

.pagination {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 16px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.params-dialog {
  border-radius: 20px;
  overflow: hidden;
}

.dialog-empty {
  padding: 40px 20px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0 0 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .services-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .mcp-services-container {
    padding: 16px;
  }
  
  .page-header {
    padding: 24px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 24px;
  }
  
  .header-actions {
    min-width: auto;
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .search-input,
  .filter-select {
    width: 100%;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .title-section {
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .header-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .search-section {
    flex-direction: column;
    gap: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 8px;
  }
  
  .search-btn,
  .refresh-btn {
    width: 100%;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .action-section {
    align-self: flex-end;
  }
  
  .meta-row {
    flex-direction: column;
    gap: 12px;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .mcp-services-container {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
  }
  
  .page-header,
  .service-card,
  .pagination {
    background: rgba(45, 55, 72, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  .page-title {
    color: #f7fafc;
  }
  
  .page-subtitle {
    color: #a0aec0;
  }
  
  .service-name {
    color: #f7fafc;
  }
  
  .service-description,
  .meta-value {
    color: #cbd5e0;
  }
  
  .url-container {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    border-color: #4a5568;
  }
  
  .url-text {
    color: #cbd5e0;
  }
  
  .add-service-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(45, 55, 72, 0.95) 100%);
  }
}
</style>