<template>
  <el-container class="marketplace-container">
    <!-- 左侧分类列表，增加宽度 -->
    <el-aside width="280px" class="pr-4">
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <el-icon class="mr-2">
                <Menu />
              </el-icon>
              <span class="text-lg font-semibold">MCP 分类</span>
            </div>
            <div>
              <el-button size="small" @click="showCreateCategoryDialog">
                <el-icon>
                  <Plus />
                </el-icon>
              </el-button>
            </div>
          </div>
        </template>

        <el-menu :default-active="activeCategory ? activeCategory.id.toString() : ''" @select="handleCategorySelect"
          class="border-0 category-menu">
          <el-menu-item index="all">
            <el-icon>
              <Collection />
            </el-icon>
            <span>全部</span>
          </el-menu-item>

          <el-menu-item v-for="category in categories" :key="category.id" :index="category.id.toString()"
            class="category-item">
            <el-icon>
              <component :is="getCategoryIcon(category)" />
            </el-icon>
            <span class="category-name">{{ category.name }}</span>
            <el-tag size="small" class="ml-auto">{{ category.modules_count || 0 }}</el-tag>
            <el-dropdown v-if="hasAdminPermission" trigger="click" @click.stop>
              <el-icon class="ml-2">
                <MoreFilled />
              </el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click.stop="handleEditCategory(category)">编辑</el-dropdown-item>
                  <el-dropdown-item @click.stop="handleDeleteCategory(category)">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-menu-item>
        </el-menu>
      </el-card>
    </el-aside>

    <!-- 右侧内容 -->
    <el-main class="p-4">
      <el-page-header class="mb-4"
        :title="activeCategory && activeCategory.id !== 'all' ? activeCategory.name : 'MCP 广场'">
        <template #extra>
          <el-button type="success" @click="showCreateDialog" class="mr-2">新建MCP服务</el-button>
          <el-button type="primary" @click="loadModules" :loading="scanning">刷新</el-button>
        </template>
      </el-page-header>

      <!-- 一行三列的卡片网格 -->
      <div class="module-grid">
        <div v-for="module in modules" :key="module.id" class="module-item">
          <el-card class="module-card" shadow="hover" @click="goToModuleDetail(module.id)">
            <div class="card-header">
              <el-avatar :icon="getModuleIcon(module)" :size="40" class="mr-2"></el-avatar>
              <h3 class="card-title">{{ module.name }}</h3>
            </div>
            <p class="card-desc">{{ module.description }}</p>
            <div class="card-footer">
              <div class="tag-container">
                <el-tag v-if="module.category_name" size="small" type="warning" class="ml-1">
                  {{ module.category_name }}
                </el-tag>
                <el-tag v-if="!module.is_public" size="small" type="danger" class="ml-1">
                  私有
                </el-tag>
                <el-tag v-else size="small" type="success" class="ml-1">
                  公开
                </el-tag>
                <el-tag v-if="module.creator_name" size="small" type="info" class="ml-1">
                  创建者: {{ module.creator_name }}
                </el-tag>
              </div>
              <div class="flex flex-col items-end">
                <div class="text-gray-500 text-xs mb-1">更新时间: {{ formatDate(module.updated_at) }}</div>
                <el-dropdown trigger="click" @click.stop>
                  <el-button size="small" type="primary" @click.stop>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click.stop="goToModuleDetail(module.id)">
                        <el-icon><View /></el-icon> 查看详情
                      </el-dropdown-item>
                      <el-dropdown-item @click.stop="handleCloneModule(module)">
                        <el-icon><CopyDocument /></el-icon> 复制
                      </el-dropdown-item>
                      <el-dropdown-item v-if="hasEditPermission(module)" @click.stop="handleDeleteModule(module)" divided>
                        <el-icon><Delete /></el-icon> 删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="modules.length === 0 && !loading" class="text-center py-10">
        <el-empty description="暂无MCP模块" />
        <el-button type="primary" @click="loadModules" class="mt-4">刷新</el-button>
      </div>

      <div v-if="loading" class="loading-container">
        <div class="module-grid">
          <div v-for="i in 6" :key="i" class="module-item">
            <el-skeleton class="p-4" :rows="3" animated />
          </div>
        </div>
      </div>
    </el-main>

    <!-- 创建MCP服务对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建MCP服务" width="60%" :destroy-on-close="true">
      <McpServiceForm 
        v-model="createForm" 
        :categories="categories"
        :isSubmitting="submitting"
        ref="createFormRef"
      >
        <template #actions>
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCreateForm" :loading="submitting">创建</el-button>
        </template>
      </McpServiceForm>
    </el-dialog>

    <!-- 复制MCP服务对话框 -->
    <el-dialog v-model="cloneDialogVisible" title="复制MCP服务" width="60%" :destroy-on-close="true">
      <McpServiceForm 
        v-model="cloneForm" 
        :categories="categories"
        :isSubmitting="submitting"
        ref="cloneFormRef"
      >
        <template #actions>
          <el-button @click="cloneDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCloneForm" :loading="submitting">复制</el-button>
        </template>
      </McpServiceForm>
    </el-dialog>

    <!-- 创建分类对话框 -->
    <el-dialog v-model="categoryDialogVisible" :title="editingCategory ? '编辑分类' : '创建分类'" width="40%"
      :destroy-on-close="true">
      <el-form ref="categoryFormRef" :model="categoryForm" :rules="categoryRules" label-width="100px"
        label-position="top">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model.trim="categoryForm.name" placeholder="请输入分类名称" clearable></el-input>
        </el-form-item>

        <el-form-item label="分类描述" prop="description">
          <el-input v-model.trim="categoryForm.description" placeholder="请输入分类描述" clearable></el-input>
        </el-form-item>

        <el-form-item label="图标" prop="icon">
          <el-select v-model="categoryForm.icon" placeholder="请选择图标" style="width: 100%">
            <el-option v-for="icon in iconOptions" :key="icon" :label="icon" :value="icon">
              <div class="flex items-center">
                <el-icon class="mr-2">
                  <component :is="icon" />
                </el-icon>
                <span>{{ icon }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="categoryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCategoryForm" :loading="submitting">
            {{ editingCategory ? '保存' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElNotification, ElMessageBox } from 'element-plus';
import {
  Tools, Menu, Collection, Plus, MoreFilled, Folder, Edit,
  Star, Box, Monitor, Setting, Document, View, CopyDocument, Delete
} from '@element-plus/icons-vue';
import {
  listModules, listGroup, createModule, deleteModule, cloneModule,
  createGroup, updateGroup, deleteGroup
} from '../../api/marketplace';
import type { McpModuleInfo, ScanResult, McpCategoryInfo } from '../../types/marketplace';
import McpServiceForm from './components/McpServiceForm.vue';

const router = useRouter();
const modules = ref<McpModuleInfo[]>([]);
const categories = ref<McpCategoryInfo[]>([]);
const loading = ref(true);
const scanning = ref(false);
const selectedCategoryId = ref<string | null>('all');

// 创建服务相关
const createDialogVisible = ref(false);
const submitting = ref(false);
const createFormRef = ref<any>();
const createForm = ref<{
  name: string;
  description: string;
  module_path: string;
  author: string;
  version: string;
  tags: string[];
  category_id: number | null;
  code: string;
  is_public: boolean;
}>({
  name: '',
  description: '',
  module_path: '',
  author: '',
  version: '1.0.0',
  tags: [] as string[],
  category_id: null,
  code: '',
  is_public: true
});

const createRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入服务描述', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入代码', trigger: 'blur' }
  ]
};

// 复制服务相关
const cloneDialogVisible = ref(false);
const cloneFormRef = ref<any>();
const cloneForm = ref<{
  name: string;
  description: string;
  version: string;
  tags: string[];
  category_id: number | null;
  is_public: boolean;
  source_module_id: number | null;
}>({
  name: '',
  description: '',
  version: '1.0.0',
  tags: [] as string[],
  category_id: null,
  is_public: true,
  source_module_id: null
});

const cloneRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入服务描述', trigger: 'blur' }
  ]
};

const activeCategory = computed(() => {
  if (selectedCategoryId.value === 'all') {
    return { id: 'all', name: '全部' };
  }
  return categories.value.find(c => c.id.toString() === selectedCategoryId.value) || null;
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

// 显示创建对话框
function showCreateDialog() {
  // 检查用户是否登录
  if (!currentUser.value.user_id) {
    ElMessageBox.alert(
      '您需要登录后才能创建MCP服务。',
      '请先登录',
      { type: 'warning' }
    );
    return;
  }

  // 重置表单数据
  createForm.value = {
    name: '',
    description: '',
    module_path: '',
    author: '',
    version: '1.0.0',
    tags: [] as string[],
    category_id: null,
    code: '',
    is_public: true
  };
  nextTick(() => {
    createDialogVisible.value = true;
  });
}

// 提交创建表单
async function submitCreateForm() {
  submitting.value = true;
  try {
    // 处理tags，转换为字符串
    const tagsStr = Array.isArray(createForm.value.tags) ? createForm.value.tags.join(',') : '';

    // 构建模块数据
    const moduleData: Partial<McpModuleInfo> = {
      name: createForm.value.name,
      description: createForm.value.description,
      module_path: createForm.value.module_path,
      author: createForm.value.author,
      version: createForm.value.version,
      tags: tagsStr,  // 使用转换后的字符串
      category_id: createForm.value.category_id || undefined,
      code: createForm.value.code,
      is_public: createForm.value.is_public,
      is_hosted: true,
      user_id: currentUser.value.user_id || undefined // 添加创建者ID
    };

    const response = await createModule(moduleData);

    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: 'MCP服务创建成功',
        type: 'success'
      });
      createDialogVisible.value = false;
      // 重新加载模块列表
      loadModules();
    } else {
      ElNotification({
        title: '错误',
        message: response?.message || '创建MCP服务失败',
        type: 'error'
      });
    }
  } catch (error) {
    console.error('创建MCP服务失败:', error);
    ElNotification({
      title: '错误',
      message: '创建MCP服务失败',
      type: 'error'
    });
  } finally {
    submitting.value = false;
  }
}

// 加载模块列表
async function loadModules() {
  loading.value = true;
  try {
    const categoryId = selectedCategoryId.value === 'all' ? null : selectedCategoryId.value;
    const response = await listModules(categoryId);
    // 处理API响应格式
    if (response && response.data) {
      modules.value = response.data;
    } else {
      modules.value = [];
    }
  } catch (error) {
    console.error("加载模块失败", error);
    ElNotification({
      title: '错误',
      message: '加载MCP模块列表失败',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
}

// 加载分组列表
async function loadCategories() {
  try {
    const response = await listGroup();
    // 处理API响应格式
    if (response && response.data) {
      categories.value = response.data;
    } else {
      categories.value = [];
    }
  } catch (error) {
    console.error("加载分组失败", error);
    ElNotification({
      title: '错误',
      message: '加载MCP分组列表失败',
      type: 'error'
    });
  }
}

// 处理分组选择
function handleCategorySelect(categoryId: string) {
  selectedCategoryId.value = categoryId;
  loadModules();
}

// 根据分组类型获取图标
function getCategoryIcon(category: McpCategoryInfo) {
  // 如果分组有自定义图标，返回
  if (category.icon) {
    return category.icon;
  }
  // 默认图标
  return 'Folder';
}

// 根据模块类型获取图标
function getModuleIcon(module: McpModuleInfo) {
  // 根据模块类型或名称返回不同的图标
  if (module.name.toLowerCase().includes('tavily')) {
    return 'Search';
  } else if (module.name.toLowerCase().includes('fetch')) {
    return 'Link';
  } else if (module.name.toLowerCase().includes('github')) {
    return 'Platform';
  } else {
    return 'Tools';
  }
}

// 跳转到模块详情页
function goToModuleDetail(moduleId: number) {
  router.push(`/marketplace/${moduleId}`);
}

// 格式化日期
function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString();
}

// 检查是否有编辑权限
function hasEditPermission(module: McpModuleInfo): boolean {
  // 如果是管理员，有权限
  if (currentUser.value.is_admin) {
    return true;
  }

  // 非管理员只能编辑自己创建的服务
  return module.user_id === currentUser.value.user_id;
}

// 处理删除模块
async function handleDeleteModule(module: McpModuleInfo) {
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
      `确定要删除"${module.name}"服务吗？删除后将无法恢复，其关联的所有服务也将被卸载。`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    ElNotification({
      title: '提示',
      message: '正在删除服务...',
      type: 'info',
      duration: 0
    });

    const response = await deleteModule(module.id);

    // 关闭所有通知
    const notifications = document.querySelectorAll('.el-notification');
    notifications.forEach(notification => {
      (notification as any).__vue__?.close();
    });

    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: '服务已删除',
        type: 'success'
      });
      // 重新加载模块列表
      await loadModules();
    } else {
      ElNotification({
        title: '错误',
        message: `删除服务失败: ${response?.message || '未知错误'}`,
        type: 'error'
      });
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElNotification({
        title: '错误',
        message: `删除服务失败: ${error.message || '未知错误'}`,
        type: 'error'
      });
    }
  }
}

// 处理复制模块
function handleCloneModule(module: McpModuleInfo) {
  // 检查用户是否登录
  if (!currentUser.value.user_id) {
    ElMessageBox.alert(
      '您需要登录后才能复制MCP服务。',
      '请先登录',
      { type: 'warning' }
    );
    return;
  }

  // 阻止事件冒泡，避免触发卡片点击事件
  event?.stopPropagation();

  // 处理标签，确保类型正确
  let tagArray: string[] = [];
  if (module.tags) {
    tagArray = typeof module.tags === 'string' ? module.tags.split(',') : module.tags;
  }

  // 设置复制表单的初始数据
  cloneForm.value = {
    name: `${module.name}_copy`,
    description: module.description || '',
    version: module.version || '1.0.0',
    tags: tagArray,
    category_id: module.category_id || null,
    is_public: module.is_public !== undefined ? module.is_public : true,
    source_module_id: module.id
  };

  nextTick(() => {
    cloneDialogVisible.value = true;
  });
}

// 提交复制表单
async function submitCloneForm() {
  submitting.value = true;
  try {
    if (!cloneForm.value.source_module_id) {
      throw new Error('源服务ID不能为空');
    }

    // 处理tags，转换为字符串
    const tagsStr = Array.isArray(cloneForm.value.tags) ? cloneForm.value.tags.join(',') : '';

    // 构建模块数据
    const moduleData: Partial<McpModuleInfo> = {
      name: cloneForm.value.name,
      description: cloneForm.value.description,
      version: cloneForm.value.version,
      tags: tagsStr,
      category_id: cloneForm.value.category_id || undefined,
      is_public: cloneForm.value.is_public,
      user_id: currentUser.value.user_id || undefined // 添加创建者ID
    };

    const response = await cloneModule(cloneForm.value.source_module_id, moduleData);

    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: 'MCP服务复制成功',
        type: 'success'
      });
      cloneDialogVisible.value = false;
      // 重新加载模块列表
      loadModules();
    } else {
      ElNotification({
        title: '错误',
        message: response?.message || '复制MCP服务失败',
        type: 'error'
      });
    }
  } catch (error) {
    console.error('复制MCP服务失败:', error);
    ElNotification({
      title: '错误',
      message: '复制MCP服务失败',
      type: 'error'
    });
  } finally {
    submitting.value = false;
  }
}

// 检查是否有管理员权限
const hasAdminPermission = computed(() => {
  return currentUser.value.is_admin;
});

// 分类管理相关
const categoryDialogVisible = ref(false);
const categoryFormRef = ref<any>();
const editingCategory = ref<McpCategoryInfo | null>(null);
const categoryForm = ref<{
  name: string;
  description: string;
  icon: string;
}>({
  name: '',
  description: '',
  icon: 'Folder'
});

const categoryRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ]
};

// 图标选项
const iconOptions = [
  'Folder', 'Document', 'Tools', 'Setting', 'Monitor', 'Box', 'Star'
];

// 显示创建分类对话框
function showCreateCategoryDialog() {
  // 检查用户是否有管理员权限
  if (!hasAdminPermission.value) {
    ElMessageBox.alert(
      '只有管理员可以创建分类。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  // 重置表单数据
  editingCategory.value = null;
  categoryForm.value = {
    name: '',
    description: '',
    icon: 'Folder'
  };
  nextTick(() => {
    categoryDialogVisible.value = true;
  });
}

// 处理编辑分类
function handleEditCategory(category: McpCategoryInfo) {
  // 检查用户是否有管理员权限
  if (!hasAdminPermission.value) {
    ElMessageBox.alert(
      '只有管理员可以编辑分类。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  // 阻止事件冒泡
  event?.stopPropagation();

  // 设置编辑表单的初始数据
  editingCategory.value = category;
  categoryForm.value = {
    name: category.name,
    description: category.description || '',
    icon: category.icon || 'Folder'
  };

  nextTick(() => {
    categoryDialogVisible.value = true;
  });
}

// 处理删除分类
async function handleDeleteCategory(category: McpCategoryInfo) {
  // 检查用户是否有管理员权限
  if (!hasAdminPermission.value) {
    ElMessageBox.alert(
      '只有管理员可以删除分类。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  // 阻止事件冒泡
  event?.stopPropagation();

  try {
    // 弹出确认框
    await ElMessageBox.confirm(
      `确定要删除"${category.name}"分类吗？删除后该分类下的MCP服务将被重置为无分类状态。`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const response = await deleteGroup(category.id);

    if (response && response.data.code === 0) {
      ElNotification({
        title: '成功',
        message: '分类已删除',
        type: 'success'
      });
      // 重新加载分类列表
      await loadCategories();
      // 如果当前选中的是被删除的分类，则切换到全部
      if (selectedCategoryId.value === category.id.toString()) {
        selectedCategoryId.value = 'all';
        await loadModules();
      }
    } else {
      ElNotification({
        title: '错误',
        message: `删除分类失败: ${response?.data?.message || '未知错误'}`,
        type: 'error'
      });
      await loadCategories();
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElNotification({
        title: '错误',
        message: `删除分类失败: ${error.message || '未知错误'}`,
        type: 'error'
      });
    }
  }
}

// 提交分类表单
async function submitCategoryForm() {
  await categoryFormRef.value?.validate(async (valid: boolean) => {
    if (!valid) return;

    submitting.value = true;
    try {
      // 构建分类数据
      const categoryData = {
        name: categoryForm.value.name,
        description: categoryForm.value.description,
        icon: categoryForm.value.icon
      };

      let response;

      if (editingCategory.value) {
        // 更新分类
        response = await updateGroup(editingCategory.value.id, categoryData);
      } else {
        // 创建分类
        response = await createGroup(categoryData);
      }
      console.log(response);
      if (response && response.data.code === 0) {
        ElNotification({
          title: '成功',
          message: editingCategory.value ? '分类已更新' : '分类已创建',
          type: 'success'
        });
        categoryDialogVisible.value = false;
        // 重新加载分类列表
        await loadCategories();
      } else {
        ElNotification({
          title: '错误',
          message: response?.data?.message || (editingCategory.value ? '更新分类失败' : '创建分类失败'),
          type: 'error'
        });
      }
    } catch (error) {
      console.error(editingCategory.value ? '更新分类失败' : '创建分类失败', error);
      ElNotification({
        title: '错误',
        message: editingCategory.value ? '更新分类失败' : '创建分类失败',
        type: 'error'
      });
    } finally {
      submitting.value = false;
    }
  });
}

// 页面加载时获取模块列表和分组列表
onMounted(async () => {
  loadUserInfo(); // 加载用户信息
  await loadCategories();
  await loadModules();
});
</script>

<style scoped>
.marketplace-container {
  height: calc(100vh - 80px);
  background-color: #f9fafc;
}

.el-aside {
  border-radius: 0 16px 16px 0;
  padding-top: 16px;
}

.el-card {
  border-radius: 16px !important;
  overflow: hidden;
}

/* 移除左侧卡片悬浮效果 */
.el-aside .el-card:hover {
  transform: none;
  box-shadow: none !important;
}

/* 只保留右侧卡片悬浮效果 */
.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.category-menu {
  max-height: calc(100vh - 150px);
  overflow-y: auto;
  border-radius: 12px;
}

.category-item {
  display: flex;
  align-items: center;
  border-radius: 8px;
  margin-bottom: 4px;
}

.el-menu-item {
  border-radius: 12px;
  margin: 4px 0;
}

.el-menu-item.is-active {
  background-color: var(--el-color-primary-light-9) !important;
}

.category-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

@media (max-width: 1400px) {
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1000px) {
  .module-grid {
    grid-template-columns: 1fr;
  }
}

.module-card {
  border-radius: 16px !important;
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  overflow: hidden;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.card-desc {
  color: #666;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 16px;
  line-height: 1.6;
  min-height: 48px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-width: 65%;
}

.el-tag {
  border-radius: 12px;
  padding: 0 10px;
}

.el-button {
  border-radius: 12px;
}

.el-button--primary {
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
}

.el-avatar {
  border-radius: 12px;
  background: linear-gradient(135deg, #e0f2ff, #d4e6fd);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.el-page-header {
  background-color: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.el-main {
  padding: 24px;
}

.el-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.loading-container {
  padding: 20px 0;
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-textarea__inner) {
  border-radius: 12px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
}

/* 添加新样式 */
.el-dropdown-menu {
  border-radius: 8px;
}

.el-dropdown {
  margin-left: 4px;
}

.el-select-dropdown__item {
  display: flex;
  align-items: center;
}
</style>