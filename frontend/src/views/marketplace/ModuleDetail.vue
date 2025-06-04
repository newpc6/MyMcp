<template>
  <div class="module-detail-container">
    <el-container class="detail-wrapper">
      <el-main class="main-content">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="10" animated />
        </div>

        <div v-else class="content-wrapper">
          <!-- 顶部信息区域 - 使用现代化卡片布局 -->
          <div class="top-cards-section">
            <!-- 模块信息卡片 -->
            <div class="module-info-section">
              <ModuleInfoCard :moduleInfo="moduleInfo" :hasEditPermission="hasEditPermission" @edit="showEditDialog"
                @delete="handleDeleteModule" @back="goBack" />
            </div>

            <!-- 服务发布卡片 -->
            <div class="service-publish-section">
              <ServicePublishCard :services="services" :loadingServices="loadingServices"
                @publish="handlePublishService" @stop-service="handleStopService" @start-service="handleStartService"
                @uninstall-service="handleUninstallService" @view-params="viewServiceParams" />
            </div>
          </div>

          <!-- 主要内容标签页 -->
          <div class="tabs-section">
            <el-card shadow="never" class="tabs-card">
              <el-tabs v-model="activeTab" class="detail-tabs">
                <el-tab-pane label="服务详情" name="service-details">
                  <div class="tab-content">
                    <ServiceDetailsPanel :moduleInfo="moduleInfo" />
                  </div>
                </el-tab-pane>

                <el-tab-pane label="工具测试" name="tool-test">
                  <div class="tab-content">
                    <ToolTestPanel :tools="moduleTools" :moduleId="moduleId" @test="handleToolTest" />
                  </div>
                </el-tab-pane>

                <el-tab-pane label="代码查看/编辑" name="code-edit">
                  <div class="tab-content">
                    <CodeEditorPanel v-model="codeContent" :originalCode="originalCode"
                      :hasEditPermission="hasEditPermission" :saving="saving" :code="!!moduleInfo.code"
                      @save="saveModuleCode" @format="formatPythonCode" />
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-card>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- 编辑模块对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑MCP服务" width="60%" :destroy-on-close="true" class="edit-dialog">
      <McpServiceForm v-model="editForm" :categories="categories" :isSubmitting="updating" ref="editFormRef">
        <template #actions>
          <div class="dialog-actions">
            <el-button @click="editDialogVisible = false" class="cancel-btn">取消</el-button>
            <el-button type="primary" @click="submitEditForm" :loading="updating" class="submit-btn">保存</el-button>
          </div>
        </template>
      </McpServiceForm>
    </el-dialog>

    <!-- 发布服务对话框 -->
    <el-dialog v-model="publishDialogVisible" title="配置并发布服务" width="50%" :destroy-on-close="true"
      class="publish-dialog">
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px" label-position="top"
        class="config-form">
        <el-form-item label="服务名称" prop="service_name"
          :rules="[{ required: true, message: '请输入服务名称', trigger: 'blur' }]">
          <el-input v-model="configForm.service_name" placeholder="请输入服务名称" class="form-input"></el-input>
        </el-form-item>
        <el-form-item label="是否公开" prop="is_public">
          <el-switch v-model="configForm.is_public" class="form-switch" />
        </el-form-item>

        <div v-if="!hasConfigSchema" class="no-config-alert">
          <el-alert type="info" :closable="false" show-icon title="此模块没有需要配置的参数，可以直接发布。" />
        </div>

        <template v-else>
          <el-alert type="warning" :closable="false" show-icon title="此模块需要配置以下参数才能发布" class="config-alert" />

          <el-divider content-position="left" class="config-divider">配置参数</el-divider>

          <div v-for="(schema, key) in moduleInfo.config_schema" :key="key" class="config-item">
            <el-form-item :label="schema.title || key" :prop="`config_params.${key}`" label-position="left"
              :rules="[{ required: schema.required, message: `请输入${schema.title || key}`, trigger: 'blur' }]">

              <div v-if="schema.type === 'integer'" class="form-field">
                <el-input-number v-model="configForm.config_params[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`" class="form-input-number" />
              </div>
              <div v-else class="form-field">
                <el-input v-if="schema.type === 'password'" v-model="configForm.config_params[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`"
                  :type="schema.type === 'password' ? 'password' : 'text'" show-password class="form-input" />
                <el-input v-else v-model="configForm.config_params[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`" class="form-input" />
              </div>
            </el-form-item>
          </div>
        </template>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="publishDialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="submitConfigForm" :loading="publishing" class="submit-btn">发布服务</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 服务参数查看/编辑对话框 -->
    <el-dialog v-model="serviceParamsDialogVisible" title="服务参数设置" width="50%" :destroy-on-close="true"
      class="params-dialog">
      <ServiceParamsManager v-if="currentService" :config-params="serviceParamsForm"
        :config-schema="moduleInfo.config_schema" @update:config-params="updateServiceParamsForm"
        ref="serviceParamsManagerRef" />
      <div v-else class="empty-params">
        <el-empty description="无法加载服务参数" :image-size="60" />
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="serviceParamsDialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="updateServiceParamsFunc" :loading="updatingParams"
            class="submit-btn">更新参数</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElNotification, ElMessage, ElMessageBox } from 'element-plus';
import {
  getModule, getModuleTools, testModuleTool, updateModule,
  listServices, publishModule, stopService, startService, uninstallService,
  testModuleFunction,
  listGroup,
  deleteModule,
  getService
} from '../../api/marketplace';
import { updateServiceParams } from '../../api/mcpServer';
import api from '../../api/index';
import type { McpModuleInfo, McpToolInfo, McpServiceInfo, McpCategoryInfo } from '../../types/marketplace';
import { Delete, Plus, Connection } from '@element-plus/icons-vue';
import { fallbackCopyTextToClipboard, copyTextToClipboard } from '../../utils/copy';

// 引入拆分的组件
import ModuleInfoCard from './components/ModuleInfoCard.vue';
import ServicePublishCard from './components/ServicePublishCard.vue';
import ServiceDetailsPanel from './components/ServiceDetailsPanel.vue';
import ToolTestPanel from './components/ToolTestPanel.vue';
import CodeEditorPanel from './components/CodeEditorPanel.vue';
import McpServiceForm from './components/McpServiceForm.vue';
// @ts-ignore
import ServiceParamsManager from '../../components/ServiceParamsManager.vue';

const route = useRoute();
const router = useRouter();
const moduleId = computed(() => Number(route.params.id));

const loading = ref(true);
const moduleInfo = ref<McpModuleInfo>({} as McpModuleInfo);
const moduleTools = ref<McpToolInfo[]>([]);
const activeTab = ref('service-details');
const codeContent = ref('');
const originalCode = ref('');
const saving = ref(false);

// 服务相关
const services = ref<McpServiceInfo[]>([]);
const loadingServices = ref(false);

// 添加编辑相关的变量
const editDialogVisible = ref(false);
const updating = ref(false);
const categories = ref<McpCategoryInfo[]>([]);
const editFormRef = ref<any>();
const editForm = ref<{
  name: string;
  description: string;
  module_path: string;
  author: string;
  version: string;
  tags: string[];
  category_id: number | null;
  code: string;
  is_public: boolean;
  markdown_docs: string;
  config_schema?: string;
}>({
  name: '',
  description: '',
  module_path: '',
  author: '',
  version: '',
  tags: [],
  category_id: null,
  code: '',
  is_public: true,
  markdown_docs: '',
  config_schema: ''
});

// 当前用户信息
const currentUser = ref<{
  user_id: number | null;
  username: string;
  is_admin: boolean;
}>({
  user_id: null,
  username: '',
  is_admin: false
});

// 检查是否有编辑权限
const hasEditPermission = computed((): boolean => {
  // 如果是管理员，有权限
  if (currentUser.value.is_admin) {
    return true;
  }

  // 非管理员只能编辑自己创建的服务
  return moduleInfo.value.user_id === currentUser.value.user_id;
});

// 配置参数相关
const configParams = ref<{
  key: string;
  type: string;
  title: string;
  description: string;
  required: boolean;
  placeholder?: string;
  default?: any;
}[]>([]);

// 服务发布相关
const publishDialogVisible = ref(false);
const configFormRef = ref<any>();
const configForm = ref<{
  service_name: string;
  is_public: boolean;
  config_params: Record<string, any>;
}>({
  service_name: '',
  is_public: false,
  config_params: {}
});
const configRules = ref<Record<string, any>>({});
const publishing = ref(false);

// 判断是否有配置模式
const hasConfigSchema = computed(() => {
  return moduleInfo.value.config_schema &&
    Object.keys(moduleInfo.value.config_schema).length > 0;
});

// 服务参数对话框相关
const serviceParamsDialogVisible = ref(false);
const currentService = ref<McpServiceInfo | null>(null);
const serviceParamsForm = ref<Record<string, any>>({});
const serviceParamsManagerRef = ref();
const updatingParams = ref(false);

// 加载模块详情
async function loadModuleInfo() {
  loading.value = true;
  try {
    const response = await getModule(moduleId.value);
    if (response && response.data) {
      moduleInfo.value = response.data;
    } else {
      moduleInfo.value = {} as McpModuleInfo;
    }

    const toolsResponse = await getModuleTools(moduleId.value);
    if (toolsResponse && toolsResponse.data) {
      moduleTools.value = toolsResponse.data;
    } else {
      moduleTools.value = [];
    }

    // 如果模块有代码，初始化编辑器内容
    if (moduleInfo.value.code) {
      codeContent.value = moduleInfo.value.code;
      originalCode.value = moduleInfo.value.code;
    }
  } catch (error) {
    console.error("加载模块详情失败", error);
    ElNotification({
      title: '错误',
      message: '加载模块详情失败',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
}

// 加载服务列表
const loadServices = async () => {
  loadingServices.value = true;
  try {
    const response = await listServices(moduleId.value);
    if (response && response.data) {
      services.value = response.data;
    } else {
      services.value = [];
    }
  } catch (error) {
    console.error('加载服务列表失败', error);
    ElMessage.error('加载服务列表失败');
  } finally {
    loadingServices.value = false;
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

// 保存模块代码
async function saveModuleCode() {
  saving.value = true;
  try {
    await updateModule(moduleId.value, { code: codeContent.value });
    originalCode.value = codeContent.value;
    ElNotification({
      title: '成功',
      message: '模块代码已保存',
      type: 'success'
    });
  } catch (error) {
    console.error("保存模块代码失败", error);
    ElNotification({
      title: '错误',
      message: '保存模块代码失败',
      type: 'error'
    });
  } finally {
    saving.value = false;
  }
}

// 格式化Python代码
function formatPythonCode() {
  // 这里实现代码格式化逻辑，可以使用工具或者API
  ElMessage.info("代码格式化功能尚未实现");
}

// 返回列表页
function goBack() {
  router.push('/marketplace');
}

// 处理发布服务
const handlePublishService = () => {
  // 初始化配置表单
  initConfigForm();
  publishDialogVisible.value = true;
};

// 初始化配置表单
function initConfigForm() {
  configForm.value = {
    service_name: `${moduleInfo.value.name}-实例-${new Date().getTime().toString().slice(-6)}`, // 默认服务名称
    is_public: false,
    config_params: {}
  };
  configRules.value = {
    service_name: [{ required: true, message: '请输入服务名称', trigger: 'blur' }]
  };

  if (moduleInfo.value.config_schema) {
    Object.entries(moduleInfo.value.config_schema).forEach(([key, schema]: [string, any]) => {
      configForm.value.config_params[key] = '';
      if (schema.required) {
        configRules.value[`config_params.${key}`] = [
          { required: true, message: `请输入${schema.title || key}`, trigger: 'blur' }
        ];
      }
    });
  }
}

// 提交配置表单
const submitConfigForm = async () => {
  if (!configFormRef.value) return;

  try {
    await configFormRef.value.validate();
    publishDialogVisible.value = false;
    publishServiceWithConfig(configForm.value);
  } catch (error) {
    console.error('表单验证失败', error);
  }
};

// 带配置参数发布服务
const publishServiceWithConfig = async (config: Record<string, any>) => {
  publishing.value = true;
  try {
    ElMessage.info({ message: '正在发布服务...', duration: 0 });
    await publishModule(moduleId.value, config);
    ElMessage.closeAll();
    ElMessage.success('服务发布成功');
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    ElMessage.error(`发布服务失败: ${error.message || '未知错误'}`);
  } finally {
    publishing.value = false;
  }
};

// 停止服务
const handleStopService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在停止服务...', duration: 0 });
    await stopService(serviceUuid);
    ElMessage.closeAll();
    ElMessage.success('服务已停止');
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    ElMessage.error(`停止服务失败: ${error.message || '未知错误'}`);
  }
};

// 启动服务
const handleStartService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在启动服务...', duration: 0 });
    await startService(serviceUuid);
    ElMessage.closeAll();
    ElMessage.success('服务已启动');
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    ElMessage.error(`启动服务失败: ${error.message || '未知错误'}`);
  }
};

// 卸载服务
const handleUninstallService = async (serviceUuid: string) => {
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
      '确定要卸载此服务吗？卸载后将无法恢复。',
      '确认卸载',
      {
        confirmButtonText: '确认卸载',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    ElMessage.info({ message: '正在卸载服务...', duration: 0 });
    await uninstallService(serviceUuid);
    ElMessage.closeAll();
    ElMessage.success('服务已卸载');
    // 重新加载服务列表
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    if (error !== 'cancel') {
      ElMessage.error(`卸载服务失败: ${error.message || '未知错误'}`);
    }
  }
};

// 加载分类列表
async function loadCategories() {
  try {
    const response = await listGroup();
    if (response && response.data) {
      categories.value = response.data;
    } else {
      categories.value = [];
    }
  } catch (error) {
    console.error("加载分类失败", error);
    ElNotification({
      title: '错误',
      message: '加载MCP分类列表失败',
      type: 'error'
    });
  }
}

// 显示编辑对话框
function showEditDialog() {
  // 检查权限
  if (!hasEditPermission.value) {
    ElMessageBox.alert(
      '您没有权限编辑此MCP服务。只有管理员或服务创建者才能编辑。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  // 加载分类数据
  loadCategories();
  // 处理tags，确保是数组
  let tagsArray: string[] = [];
  if (typeof moduleInfo.value.tags === 'string') {
    tagsArray = moduleInfo.value.tags.split(',').filter(t => t.trim());
  } else if (Array.isArray(moduleInfo.value.tags)) {
    tagsArray = moduleInfo.value.tags;
  }

  // 处理配置参数
  // configParams.value = [];
  // if (moduleInfo.value.config_schema) {
  //   // 将配置转换为参数列表
  //   Object.entries(moduleInfo.value.config_schema).forEach(([key, config]: [string, any]) => {
  //     configParams.value.push({
  //       key,
  //       type: config.type || 'string',
  //       title: config.title || '',
  //       description: config.description || '',
  //       required: config.required || false,
  //       placeholder: config.placeholder || '',
  //       default: config.default
  //     });
  //   });
  // }

  // 填充表单数据，确保每个字段都有默认值
  editForm.value = {
    name: moduleInfo.value.name || '',
    description: moduleInfo.value.description || '',
    module_path: moduleInfo.value.module_path || '',
    author: moduleInfo.value.author || '',
    version: moduleInfo.value.version || '',
    tags: tagsArray,
    category_id: moduleInfo.value.category_id || null,
    code: moduleInfo.value.code || '',
    is_public: moduleInfo.value.is_public === false ? false : true,
    markdown_docs: moduleInfo.value.markdown_docs || '',
    config_schema: moduleInfo.value.config_schema ? JSON.stringify(moduleInfo.value.config_schema, null, 2) : ''
  };
  console.log('editForm', editForm.value)

  nextTick(() => {
    editDialogVisible.value = true;
  });
}

// 提交编辑表单
async function submitEditForm() {
  updating.value = true;
  try {
    // 处理tags，转换为字符串
    const tagsStr = Array.isArray(editForm.value.tags) ? editForm.value.tags.join(',') : '';

    // 构建要更新的数据
    const moduleData: Partial<McpModuleInfo> = {
      name: editForm.value.name,
      description: editForm.value.description,
      module_path: editForm.value.module_path,
      author: editForm.value.author,
      version: editForm.value.version,
      tags: tagsStr,
      category_id: editForm.value.category_id || undefined,
      code: editForm.value.code,
      is_public: Boolean(editForm.value.is_public),
      markdown_docs: editForm.value.markdown_docs,
      config_schema: editForm.value.config_schema ? JSON.parse(editForm.value.config_schema) : undefined
    };

    const response = await updateModule(moduleInfo.value.id, moduleData);

    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: 'MCP服务更新成功',
        type: 'success'
      });
      editDialogVisible.value = false;

      // 重新加载模块详情
      loadModuleInfo();
    } else {
      ElNotification({
        title: '错误',
        message: response?.message || '更新MCP服务失败',
        type: 'error'
      });
    }
  } catch (error) {
    console.error('更新MCP服务失败:', error);
    ElNotification({
      title: '错误',
      message: '更新MCP服务失败',
      type: 'error'
    });
  } finally {
    updating.value = false;
  }
}

// 处理删除模块
async function handleDeleteModule() {
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
      '确定要删除此MCP服务吗？删除后将无法恢复，其关联的所有服务也将被卸载。',
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    ElMessage.info({ message: '正在删除服务...', duration: 0 });
    const response = await deleteModule(moduleId.value);
    ElMessage.closeAll();
    if (response && response.code === 0) {
      ElMessage.success('服务已删除');
      // 删除成功后，返回到广场页面
      router.push('/marketplace');
    } else {
      ElMessage.error(`删除服务失败: ${response?.message || '未知错误'}`);
    }
  } catch (error: any) {
    ElMessage.closeAll();
    if (error !== 'cancel') {
      ElMessage.error(`删除服务失败: ${error.message || '未知错误'}`);
    }
  }
}

// 查看服务参数
const viewServiceParams = async (service: McpServiceInfo) => {
  try {
    // 获取最新的服务信息
    const response = await getService(service.service_uuid);
    if (response && response.data) {
      currentService.value = response.data;
      // 初始化表单
      serviceParamsForm.value = { ...response.data.config_params };
      serviceParamsDialogVisible.value = true;
    }
  } catch (error) {
    console.error('获取服务参数失败', error);
    ElMessage.error('获取服务参数失败');
  }
};

// 获取参数显示名称
const getParamDisplay = (key: string): string => {
  if (!moduleInfo.value.config_schema) return key;

  const schema = moduleInfo.value.config_schema[key];
  if (schema && schema.title) {
    return schema.title;
  }
  return key;
};

// 获取参数描述
const getParamDescription = (key: string): string => {
  if (!moduleInfo.value.config_schema) return '';

  const schema = moduleInfo.value.config_schema[key];
  if (schema && schema.description) {
    return schema.description;
  }
  return '';
};

// 获取参数类型
const getParamType = (key: string): string => {
  if (!moduleInfo.value.config_schema) return 'string';

  const schema = moduleInfo.value.config_schema[key];
  if (schema && schema.type) {
    return schema.type;
  }
  return 'string';
};

// 获取参数占位符
const getParamPlaceholder = (key: string): string => {
  if (!moduleInfo.value.config_schema) return '';

  const schema = moduleInfo.value.config_schema[key];
  if (schema && schema.placeholder) {
    return schema.placeholder;
  }
  return '';
};

// 更新服务参数表单
const updateServiceParamsForm = (newParams: Record<string, any>) => {
  serviceParamsForm.value = { ...newParams };
};

// 更新服务参数
const updateServiceParamsFunc = async () => {
  if (!currentService.value) return;

  // updatingParams.value = true;
  try {
    // 调用API更新服务参数
    await updateServiceParams(currentService.value.id, serviceParamsForm.value);
    ElMessage.success('服务参数更新成功');
    serviceParamsDialogVisible.value = false;

    // 重新加载服务列表
    await loadServices();
  } catch (error) {
    console.error('更新服务参数失败', error);
    ElMessage.error('更新服务参数失败');
  } finally {
    // updatingParams.value = false;
  }
};

// 工具测试包装函数
const handleToolTest = (toolName: string, params: Record<string, any>, callback: (result: any, error?: any) => void) => {
  testModuleFunction(moduleId.value, toolName, params)
    .then(response => {
      callback(response.data);
    })
    .catch(error => {
      callback(null, error);
    });
};

// 页面加载时获取模块详情
onMounted(() => {
  loadUserInfo(); // 加载用户信息
  loadModuleInfo();
  loadServices(); // 添加加载服务
});
</script>

<style scoped>
/* 主容器样式 */
.module-detail-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.detail-wrapper {
  max-width: calc(100% - 40px);
  margin: 0 auto;
}

.main-content {
  padding: 0;
}

.loading-container {
  padding: 40px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 顶部卡片区域 */
.top-cards-section {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  align-items: stretch;
  /* 确保卡片高度一致 */
}

.module-info-section {
  flex: 2;
  /* 占据2/5的宽度 */
  min-height: 330px;
}

.service-publish-section {
  flex: 3;
  /* 占据3/5的宽度 */
  min-height: 330px;
}

.module-info-section :deep(.el-card),
.service-publish-section :deep(.el-card) {
  height: 100%;
  /* 确保卡片填满容器高度 */
  display: flex;
  flex-direction: column;
}

.module-info-section :deep(.el-card__body),
.service-publish-section :deep(.el-card__body) {
  flex: 1;
  /* 让卡片内容区域自动填充剩余空间 */
  display: flex;
  flex-direction: column;
}

/* 标签页区域 */
.tabs-section {
  flex: 1;
}

.tabs-card {
  border-radius: 20px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(235, 235, 235, 0.6);
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
  backdrop-filter: blur(10px);
}

.detail-tabs {
  padding: 0 8px;
}

:deep(.el-tabs__header) {
  margin: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 2px solid rgba(59, 130, 246, 0.1);
  border-radius: 20px 20px 0 0;
  padding: 0 20px;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0 24px;
  height: 56px;
  line-height: 56px;
  font-size: 15px;
  font-weight: 500;
  color: #64748b;
  border-radius: 12px;
  margin: 8px 4px;
  position: relative;
  overflow: hidden;
}

:deep(.el-tabs__item::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 197, 253, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 12px;
}

:deep(.el-tabs__item:hover) {
  color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

:deep(.el-tabs__item:hover::before) {
  opacity: 1;
}

:deep(.el-tabs__item.is-active) {
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
  transform: translateY(-3px);
}

:deep(.el-tabs__item.is-active::before) {
  opacity: 0;
}

:deep(.el-tabs__active-bar) {
  display: none;
}

.tab-content {
  padding: 24px;
  min-height: 400px;
}

/* 对话框样式 */
.edit-dialog :deep(.el-dialog),
.publish-dialog :deep(.el-dialog),
.params-dialog :deep(.el-dialog) {
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
  overflow: hidden;
}

.edit-dialog :deep(.el-dialog__header),
.publish-dialog :deep(.el-dialog__header),
.params-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 24px 32px;
  border-bottom: 1px solid rgba(235, 235, 235, 0.8);
}

.edit-dialog :deep(.el-dialog__title),
.publish-dialog :deep(.el-dialog__title),
.params-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.edit-dialog :deep(.el-dialog__body),
.publish-dialog :deep(.el-dialog__body),
.params-dialog :deep(.el-dialog__body) {
  padding: 32px;
}

/* 表单样式 */
.config-form {
  padding: 0;
}

.form-input,
.form-input-number {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.form-input :deep(.el-input__wrapper),
.form-input-number :deep(.el-input-number__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.form-input :deep(.el-input__wrapper:hover),
.form-input-number :deep(.el-input-number__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

.form-input :deep(.el-input__wrapper.is-focus),
.form-input-number :deep(.el-input-number__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-switch :deep(.el-switch__core) {
  border-radius: 20px;
  transition: all 0.3s ease;
}

.form-switch :deep(.el-switch.is-checked .el-switch__core) {
  background: linear-gradient(135deg, #10b981, #059669);
}

/* 警告和提示样式 */
.no-config-alert,
.config-alert {
  margin: 20px 0;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.config-divider {
  margin: 24px 0;
  font-weight: 600;
  color: #374151;
}

.config-item {
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(248, 250, 252, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(235, 235, 235, 0.6);
  transition: all 0.3s ease;
}

.config-item:hover {
  background: rgba(248, 250, 252, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.form-field {
  width: 100%;
}

/* 按钮样式 */
.dialog-actions,
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 0 0 0;
  border-top: 1px solid rgba(235, 235, 235, 0.6);
  margin-top: 24px;
}

.cancel-btn {
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 2px solid #e5e7eb;
  background: #ffffff;
  color: #6b7280;
}

.cancel-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.submit-btn {
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 空状态样式 */
.empty-params {
  text-align: center;
  padding: 40px 20px;
  background: rgba(248, 250, 252, 0.5);
  border-radius: 16px;
  border: 2px dashed rgba(203, 213, 225, 0.8);
}

.empty-params :deep(.el-empty) {
  padding: 20px 0;
}

.empty-params :deep(.el-empty__description) {
  color: #64748b;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .top-cards-section {
    flex-direction: column;
    gap: 20px;
  }

  .module-info-section,
  .service-publish-section {
    flex: 1;
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .module-detail-container {
    padding: 12px;
  }

  .content-wrapper {
    gap: 16px;
  }

  .tab-content {
    padding: 16px;
  }

  .edit-dialog :deep(.el-dialog),
  .publish-dialog :deep(.el-dialog),
  .params-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }

  :deep(.el-tabs__item) {
    padding: 0 16px;
    font-size: 14px;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-wrapper {
  animation: fadeInUp 0.6s ease-out;
}

.top-cards-section>div {
  animation: fadeInUp 0.6s ease-out;
}

.top-cards-section>div:nth-child(2) {
  animation-delay: 0.1s;
}

.tabs-section {
  animation: fadeInUp 0.6s ease-out 0.2s both;
}
</style>