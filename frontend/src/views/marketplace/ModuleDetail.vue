<template>
  <el-container class="p-4">
    <el-main class="p-0">
      <div v-if="loading" class="py-10">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else>
        <!-- 顶部信息区域 - 使用flex布局水平排列两个卡片 -->
        <div class="flex gap-4 mb-4">
          <!-- 模块信息卡片 -->
          <ModuleInfoCard 
            :moduleInfo="moduleInfo" 
            :hasEditPermission="hasEditPermission"
            @edit="showEditDialog"
            @delete="handleDeleteModule"
            @back="goBack"
            style="width: 45%"
          />

          <!-- 服务发布卡片 -->
          <ServicePublishCard 
            :services="services" 
            :loadingServices="loadingServices"
            @publish="handlePublishService"
            @stop-service="handleStopService"
            @start-service="handleStartService"
            @uninstall-service="handleUninstallService"
            @view-params="viewServiceParams"
            style="width: 55%"
          />
        </div>

        <!-- 标签页 -->
        <el-card shadow="never" class="tabs-card">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="服务详情" name="service-details">
              <ServiceDetailsPanel :moduleInfo="moduleInfo" />
            </el-tab-pane>

            <el-tab-pane label="工具测试" name="tool-test">
              <ToolTestPanel 
                :tools="moduleTools" 
                :moduleId="moduleId"
                @test="handleToolTest"
              />
            </el-tab-pane>

            <el-tab-pane label="代码查看/编辑" name="code-edit">
              <CodeEditorPanel 
                v-model="codeContent"
                :originalCode="originalCode"
                :hasEditPermission="hasEditPermission"
                :saving="saving"
                :code="!!moduleInfo.code"
                @save="saveModuleCode"
                @format="formatPythonCode"
              />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </el-main>

    <!-- 编辑模块对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑MCP服务" width="60%" :destroy-on-close="true">
      <McpServiceForm 
        v-model="editForm" 
        :categories="categories"
        :isSubmitting="updating"
        ref="editFormRef"
      >
        <template #actions>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditForm" :loading="updating">保存</el-button>
        </template>
      </McpServiceForm>
    </el-dialog>

    <!-- 发布服务对话框 -->
    <el-dialog v-model="publishDialogVisible" title="配置并发布服务" width="50%" :destroy-on-close="true">
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px" label-position="top">
        <el-form-item label="服务名称" prop="service_name" :rules="[{ required: true, message: '请输入服务名称', trigger: 'blur' }]">
          <el-input v-model="configForm.service_name" placeholder="请输入服务名称"></el-input>
        </el-form-item>
        <el-form-item label="是否公开" prop="is_public">
          <el-switch v-model="configForm.is_public" />
        </el-form-item>
        <div v-if="!hasConfigSchema">
          <el-alert type="info" :closable="false" show-icon title="此模块没有需要配置的参数，可以直接发布。" class="mb-4" />
        </div>

        <template v-else>
          <el-alert type="warning" :closable="false" show-icon title="此模块需要配置以下参数才能发布" class="mb-4" />

          <el-divider content-position="left">配置参数</el-divider>

          <div v-for="(schema, key) in moduleInfo.config_schema" :key="key" class="mb-4">
            <el-form-item :label="schema.title || key" :prop="`config_params.${key}`" label-position="left"
              :rules="[{ required: schema.required, message: `请输入${schema.title || key}`, trigger: 'blur' }]">

              <!-- <div class="text-sm text-gray-500 mb-1">{{ schema.description }}</div> -->
              <div v-if="schema.type === 'integer'">
                <el-input-number v-model="configForm.config_params[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`" />
              </div>
              <div v-else>
                <el-input v-if="schema.type === 'password'" v-model="configForm.config_params[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`"
                  :type="schema.type === 'password' ? 'password' : 'text'" show-password />
                <el-input v-else v-model="configForm.config_params[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`" />
              </div>
            </el-form-item>
          </div>
        </template>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="publishDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitConfigForm" :loading="publishing">发布服务</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 服务参数查看/编辑对话框 -->
    <el-dialog v-model="serviceParamsDialogVisible" title="服务参数设置" width="50%" :destroy-on-close="true">
      <div v-if="currentService">
        <div v-if="!currentService.config_params || Object.keys(currentService.config_params).length === 0"
          class="text-center py-4">
          <el-empty description="此服务没有配置参数" :image-size="60" />
        </div>
        <div v-else>
          <el-form ref="serviceParamsFormRef" :model="serviceParamsForm" label-width="120px" label-position="top">
            <div v-for="(value, key) in currentService.config_params" :key="key" class="mb-4">
              <el-form-item :label="getParamDisplay(key)" label-position="left">
                <div v-if="isNumeric(value)">
                  <el-input-number v-model="serviceParamsForm[key]" />
                </div>
                <div v-else-if="isBoolean(value)">
                  <el-switch v-model="serviceParamsForm[key]" />
                </div>
                <div v-else>
                  <el-input v-if="isPassword(key)" v-model="serviceParamsForm[key]" type="password" show-password />
                  <el-input v-else v-model="serviceParamsForm[key]" />
                </div>
              </el-form-item>
            </div>
          </el-form>
        </div>
      </div>
      <div v-else class="text-center py-4">
        <el-empty description="无法加载服务参数" :image-size="60" />
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="serviceParamsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateServiceParamsFunc" :loading="updatingParams">更新参数</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
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
  category_id: number | undefined;
  code: string;
  is_public: boolean;
  markdown_docs: string;
}>({
  name: '',
  description: '',
  module_path: '',
  author: '',
  version: '',
  tags: [],
  category_id: undefined,
  code: '',
  is_public: true,
  markdown_docs: ''
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

    // 处理config_schema
    if (moduleInfo.value.config_schema) {
      try {
        // 先确保config_schema是对象格式
        let schema: Record<string, any>;
        if (typeof moduleInfo.value.config_schema === 'string') {
          schema = JSON.parse(moduleInfo.value.config_schema);
        } else {
          schema = moduleInfo.value.config_schema;
        }

        Object.entries(schema).forEach(([key, config]: [string, any]) => {
          configParams.value.push({
            key,
            type: config.type || 'string',
            title: config.title || '',
            description: config.description || '',
            required: config.required || false,
            placeholder: config.placeholder || '',
            default: config.default
          });
        });
      } catch (e) {
        console.error('解析配置模式失败', e);
        ElMessage.error('配置模式解析失败');
      }
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

// 生成config_schema对象
function generateConfigSchema(): Record<string, any> {
  const schema: Record<string, any> = {};

  configParams.value.forEach(param => {
    if (!param.key) return;

    schema[param.key] = {
      type: param.type,
      description: param.description,
      required: param.required
    };

    if (param.title) {
      schema[param.key].title = param.title;
    }

    if (param.placeholder && (param.type === 'string' || param.type === 'password')) {
      schema[param.key].placeholder = param.placeholder;
    }

    if (param.default !== undefined && param.default !== null) {
      schema[param.key].default = param.default;
    }
  });

  return schema;
}

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
  configParams.value = [];
  if (moduleInfo.value.config_schema) {
    // 将配置转换为参数列表
    Object.entries(moduleInfo.value.config_schema).forEach(([key, config]: [string, any]) => {
      configParams.value.push({
        key,
        type: config.type || 'string',
        title: config.title || '',
        description: config.description || '',
        required: config.required || false,
        placeholder: config.placeholder || '',
        default: config.default
      });
    });
  }

  // 填充表单数据，确保每个字段都有默认值
  editForm.value = {
    name: moduleInfo.value.name || '',
    description: moduleInfo.value.description || '',
    module_path: moduleInfo.value.module_path || '',
    author: moduleInfo.value.author || '',
    version: moduleInfo.value.version || '',
    tags: tagsArray,
    category_id: moduleInfo.value.category_id || undefined,
    code: moduleInfo.value.code || '',
    is_public: moduleInfo.value.is_public === false ? false : true,
    markdown_docs: moduleInfo.value.markdown_docs || ''
  };

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
      category_id: editForm.value.category_id,
      code: editForm.value.code,
      is_public: Boolean(editForm.value.is_public),
      markdown_docs: editForm.value.markdown_docs,
      config_schema: generateConfigSchema()
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

// 判断值类型
const isNumeric = (value: any): boolean => {
  return typeof value === 'number';
};

const isBoolean = (value: any): boolean => {
  return typeof value === 'boolean';
};

const isPassword = (key: string): boolean => {
  if (!moduleInfo.value.config_schema) return false;

  const schema = moduleInfo.value.config_schema[key];
  return schema && schema.type === 'password';
};

// 更新服务参数
const updateServiceParamsFunc = async () => {
  if (!currentService.value) return;

  updatingParams.value = true;
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
    updatingParams.value = false;
  }
};

// 添加配置参数
function addConfigParam() {
  configParams.value.push({
    key: '',
    type: 'string',
    title: '',
    description: '',
    required: false
  });
}

// 移除配置参数
function removeConfigParam(index: number) {
  configParams.value.splice(index, 1);
}

// 工具测试包装函数
const handleToolTest = async (toolName: string, params: Record<string, any>): Promise<any> => {
  try {
    const response = await testModuleFunction(moduleId.value, toolName, params);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// 页面加载时获取模块详情
onMounted(() => {
  loadUserInfo(); // 加载用户信息
  loadModuleInfo();
  loadServices(); // 添加加载服务
});
</script>

<style scoped>
.tabs-card {
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  overflow: hidden;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: rgba(235, 235, 235, 0.8);
}

:deep(.el-tabs__item) {
  transition: all 0.3s ease;
  padding: 0 20px;
  height: 46px;
  line-height: 46px;
}

:deep(.el-tabs__item.is-active) {
  font-weight: 600;
  color: #409eff;
  transform: translateY(-2px);
}

:deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, #409eff, #79bbff);
}

:deep(.el-tab-pane) {
  padding: 16px 8px;
}

:deep(.el-empty) {
  padding: 32px 0;
  border-radius: 16px;
  background: rgba(250, 250, 250, 0.5);
  transition: all 0.3s ease;
}
</style>