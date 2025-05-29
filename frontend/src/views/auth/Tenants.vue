<template>
  <div class="tenants-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon">
            <el-icon>
              <OfficeBuilding />
            </el-icon>
          </div>
          <div class="title-text">
            <h1>租户管理</h1>
            <p>管理系统中的所有租户信息和层级关系</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" size="large" @click="handleAddTenant" class="add-btn">
            <el-icon>
              <Plus />
            </el-icon>
            新增租户
          </el-button>
        </div>
      </div>
    </div>

    <!-- 租户树容器 -->
    <div class="tenants-content">
      <div class="tree-container">
        <div class="tree-header">
          <div class="tree-title">
            <el-icon>
              <Grid />
            </el-icon>
            <span>租户层级结构</span>
          </div>
          <div class="tree-stats">
            <span class="stat-item">
              <el-icon>
                <User />
              </el-icon>
              共 {{ flattenedTenants.length }} 个租户
            </span>
          </div>
        </div>

        <el-tree v-loading="loading" :data="tenantTree" node-key="id" default-expand-all :props="defaultProps"
          class="tenant-tree" element-loading-text="加载中..." element-loading-background="rgba(255, 255, 255, 0.8)">
          <template #default="{ data }">
            <div class="tenant-card">
              <div class="tenant-avatar">
                <div class="avatar-icon" :class="getAvatarClass(data)">
                  <el-icon>
                    <OfficeBuilding />
                  </el-icon>
                </div>
              </div>

              <div class="tenant-info">
                <div class="tenant-header">
                  <h3 class="tenant-name">{{ data.name }}</h3>
                  <div class="tenant-badges">
                    <el-tag size="small" :type="data.status === 'active' ? 'success' : 'warning'" class="status-tag"
                      effect="light">
                      {{ data.status === 'active' ? '启用' : '禁用' }}
                    </el-tag>
                    <el-tag size="small" type="info" class="code-tag" effect="plain">
                      {{ data.code }}
                    </el-tag>
                  </div>
                </div>

                <div class="tenant-description" v-if="data.description">
                  <el-icon>
                    <Document />
                  </el-icon>
                  <span>{{ data.description }}</span>
                </div>

                <div class="tenant-meta">
                  <div class="meta-item" v-if="data.children && data.children.length > 0">
                    <el-icon>
                      <Folder />
                    </el-icon>
                    <span>{{ data.children.length }} 个子租户</span>
                  </div>
                  <div class="meta-item">
                    <el-icon>
                      <Clock />
                    </el-icon>
                    <span>{{ formatDate(data.created_at) }}</span>
                  </div>
                </div>
              </div>

              <div class="tenant-actions">
                <el-tooltip content="添加子租户" placement="top">
                  <el-button size="small" @click.stop="handleAddSubTenant(data)" type="success" circle
                    class="action-btn">
                    <el-icon>
                      <Plus />
                    </el-icon>
                  </el-button>
                </el-tooltip>

                <el-tooltip content="编辑租户" placement="top">
                  <el-button size="small" @click.stop="handleEditTenant(data)" :disabled="data.code === 'default'"
                    type="primary" circle class="action-btn">
                    <el-icon>
                      <Edit />
                    </el-icon>
                  </el-button>
                </el-tooltip>

                <el-tooltip content="删除租户" placement="top">
                  <el-button size="small" type="danger" @click.stop="handleDeleteTenant(data)"
                    :disabled="data.code === 'default'" circle class="action-btn">
                    <el-icon>
                      <Delete />
                    </el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </div>
          </template>
        </el-tree>
      </div>
    </div>

    <!-- 租户表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑租户' : (isSubTenant ? '新增子租户' : '新增租户')" width="600px"
      class="tenant-dialog" :close-on-click-modal="false">
      <div class="dialog-content">
        <el-form ref="tenantFormRef" :model="tenantForm" :rules="tenantRules" label-width="120px" class="tenant-form">
          <div class="form-section">
            <div class="section-title">
              <el-icon>
                <InfoFilled />
              </el-icon>
              <span>基本信息</span>
            </div>

            <el-form-item label="租户名称" prop="name">
              <el-input v-model="tenantForm.name" placeholder="请输入租户名称" size="large" />
            </el-form-item>

            <el-form-item label="租户代码" prop="code" v-if="!isEdit">
              <el-input v-model="tenantForm.code" placeholder="请输入租户代码（仅支持小写字母、数字、下划线和连字符）" size="large" />
            </el-form-item>
            <el-form-item label="租户代码" v-else>
              <el-input v-model="tenantForm.code" disabled size="large" />
            </el-form-item>

            <el-form-item label="描述信息" prop="description">
              <el-input v-model="tenantForm.description" type="textarea" :rows="3" placeholder="请输入租户描述信息"
                size="large" />
            </el-form-item>
          </div>

          <div class="form-section">
            <div class="section-title">
              <el-icon>
                <Setting />
              </el-icon>
              <span>配置信息</span>
            </div>

            <el-form-item label="上级租户" v-if="!isEdit">
              <el-select v-model="tenantForm.parent_id" clearable style="width: 100%" placeholder="请选择上级租户"
                size="large">
                <el-option label="无上级租户" :value="null" />
                <el-option v-for="tenant in flattenedTenants" :key="tenant.id" :label="tenant.name"
                  :value="tenant.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="上级租户" v-else>
              <el-select v-model="tenantForm.parent_id" clearable style="width: 100%"
                :disabled="tenantForm.code === 'default'" placeholder="请选择上级租户" size="large">
                <el-option label="无上级租户" :value="null" />
                <el-option v-for="tenant in flattenedTenants.filter(t => t.id !== tenantForm.id)" :key="tenant.id"
                  :label="tenant.name" :value="tenant.id" />
              </el-select>
            </el-form-item>

            <el-form-item label="状态" prop="status" v-if="isEdit">
              <el-select v-model="tenantForm.status" style="width: 100%" size="large">
                <el-option label="启用" value="active" />
                <el-option label="禁用" value="inactive" />
              </el-select>
            </el-form-item>
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="saveTenant" :loading="saveLoading" size="large">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import {
  Plus,
  Edit,
  Delete,
  OfficeBuilding,
  User,
  Document,
  Clock,
  Folder,
  Grid,
  InfoFilled,
  Setting
} from '@element-plus/icons-vue';
import {
  getAllTenants,
  getTenantTree,
  createTenant,
  updateTenant,
  deleteTenant
} from '@/api/auth';

// 状态
const loading = ref(false);
const tenants = ref<any[]>([]);
const tenantTree = ref<any[]>([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const isSubTenant = ref(false);
const saveLoading = ref(false);

// 租户表单
const tenantFormRef = ref<FormInstance>();
const tenantForm = reactive({
  id: null as number | null,
  name: '',
  code: '',
  description: '',
  status: 'active',
  parent_id: null as number | null
});

// 验证规则
const tenantRules = {
  name: [
    { required: true, message: '请输入租户名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    {
      required: true,
      message: '请输入租户代码',
      trigger: 'blur'
    },
    {
      pattern: /^[a-z0-9_-]+$/,
      message: '租户代码只能包含小写字母、数字、下划线和连字符',
      trigger: 'blur'
    }
  ]
};

// Tree配置
const defaultProps = {
  children: 'children',
  label: 'name',
};

// 将树形结构扁平化为列表，用于选择上级租户
const flattenedTenants = computed(() => {
  const flattened: any[] = [];

  const flatten = (nodes: any[]) => {
    for (const node of nodes) {
      flattened.push({
        id: node.id,
        name: node.name
      });

      if (node.children && node.children.length > 0) {
        flatten(node.children);
      }
    }
  };

  flatten(tenantTree.value);
  return flattened;
});

// 获取头像样式类
const getAvatarClass = (tenant: any) => {
  if (tenant.code === 'default') return 'avatar-default';
  if (tenant.status === 'active') return 'avatar-active';
  return 'avatar-inactive';
};

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};

// 初始化
onMounted(async () => {
  await fetchTenants();
});

// 获取所有租户
const fetchTenants = async () => {
  loading.value = true;
  try {
    // 获取平铺的租户列表（用于表单下拉选择）
    const tenantsResponse = await getAllTenants();
    tenants.value = tenantsResponse.data;

    // 获取租户树
    const treeResponse = await getTenantTree();
    tenantTree.value = treeResponse.data;
  } catch (error: any) {
    ElMessage.error('获取租户列表失败: ' + (error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
};

// 新增租户
const handleAddTenant = () => {
  isEdit.value = false;
  isSubTenant.value = false;
  resetTenantForm();
  dialogVisible.value = true;
};

// 新增子租户
const handleAddSubTenant = (parentTenant: any) => {
  isEdit.value = false;
  isSubTenant.value = true;
  resetTenantForm();
  tenantForm.parent_id = parentTenant.id;
  dialogVisible.value = true;
};

// 重置表单
const resetTenantForm = () => {
  tenantForm.id = null;
  tenantForm.name = '';
  tenantForm.code = '';
  tenantForm.description = '';
  tenantForm.status = 'active';
  tenantForm.parent_id = null;
};

// 编辑租户
const handleEditTenant = (row: any) => {
  isEdit.value = true;
  isSubTenant.value = false;
  tenantForm.id = row.id;
  tenantForm.name = row.name;
  tenantForm.code = row.code;
  tenantForm.description = row.description || '';
  tenantForm.status = row.status;
  tenantForm.parent_id = row.parent_id;
  dialogVisible.value = true;
};

// 删除租户
const handleDeleteTenant = (row: any) => {
  ElMessageBox.confirm(
    `确定删除租户 "${row.name}" 吗？此操作不可撤销，且将解除与用户的关联！`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const data = await deleteTenant(row.id);
      if (data.code === 0) {
        ElMessage.success('删除成功');
        await fetchTenants();
      } else {
        ElMessage.error(data.message || '删除失败');
      }
    } catch (error: any) {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'));
    }
  }).catch(() => { });
};

// 保存租户
const saveTenant = async () => {
  if (!tenantFormRef.value) return;

  try {
    await tenantFormRef.value.validate();

    saveLoading.value = true;

    // 准备提交的数据
    const tenantData: any = {
      name: tenantForm.name,
      description: tenantForm.description,
      parent_id: tenantForm.parent_id
    };

    // 如果是新增模式，则加入代码字段
    if (!isEdit.value) {
      tenantData.code = tenantForm.code;
    }

    // 如果是编辑模式，则加入状态字段
    if (isEdit.value) {
      tenantData.status = tenantForm.status;
    }

    let data;
    if (isEdit.value) {
      data = await updateTenant(tenantForm.id!, tenantData);
    } else {
      data = await createTenant(tenantData);
    }

    if (data.code === 0) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
      dialogVisible.value = false;
      await fetchTenants();
    } else {
      ElMessage.error(data.message || (isEdit.value ? '更新失败' : '创建失败'));
    }
  } catch (error: any) {
    if (error.response) {
      ElMessage.error(error.response.data.error || '操作失败');
    } else {
      ElMessage.error('操作失败: ' + (error.message || '未知错误'));
    }
  } finally {
    saveLoading.value = false;
  }
};
</script>

<style scoped lang="scss">
.tenants-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
  padding: 0;
}

// 页面头部
.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 24px 32px;
  margin-bottom: 24px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;
  }

  .header-title {
    display: flex;
    align-items: center;
    gap: 16px;

    .title-icon {
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 24px;
    }

    .title-text {
      h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        line-height: 1.2;
      }

      p {
        margin: 4px 0 0 0;
        color: #64748b;
        font-size: 14px;
      }
    }
  }

  .header-actions {
    .add-btn {
      height: 44px;
      padding: 0 24px;
      font-size: 16px;
      border-radius: 22px;
      background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
      border: none;
      box-shadow: 0 4px 15px rgba(79, 156, 249, 0.4);
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 156, 249, 0.6);
      }
    }
  }
}

// 内容区域
.tenants-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px 32px;
}

.tree-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tree-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  justify-content: space-between;
  align-items: center;

  .tree-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
    color: #334155;

    .el-icon {
      font-size: 20px;
      color: #4f9cf9;
    }
  }

  .tree-stats {
    .stat-item {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #64748b;
      font-size: 14px;

      .el-icon {
        font-size: 16px;
      }
    }
  }
}

// 租户树样式
.tenant-tree {
  padding: 24px;
  background: transparent;

  :deep(.el-tree-node__content) {
    height: auto;
    padding: 0;
    background: transparent;
    border: none;

    &:hover {
      background: transparent;
    }
  }

  :deep(.el-tree-node__expand-icon) {
    color: #4f9cf9;
    font-size: 16px;
  }

  :deep(.el-tree-node) {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

// 租户卡片
.tenant-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4f9cf9 0%, #1e40af 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    border-color: #4f9cf9;

    &::before {
      opacity: 1;
    }
  }
}

.tenant-avatar {
  .avatar-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;

    &.avatar-default {
      background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    }

    &.avatar-active {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }

    &.avatar-inactive {
      background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
    }
  }
}

.tenant-info {
  flex: 1;
  min-width: 0;
}

.tenant-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;

  .tenant-name {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    line-height: 1.3;
  }

  .tenant-badges {
    display: flex;
    gap: 8px;

    .status-tag {
      border-radius: 6px;
      font-weight: 500;
    }

    .code-tag {
      border-radius: 6px;
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 12px;
    }
  }
}

.tenant-description {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.4;

  .el-icon {
    font-size: 14px;
    color: #94a3b8;
    flex-shrink: 0;
  }
}

.tenant-meta {
  display: flex;
  gap: 16px;

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #94a3b8;
    font-size: 12px;

    .el-icon {
      font-size: 12px;
    }
  }
}

.tenant-actions {
  display: flex;
  gap: 8px;

  .action-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      transform: scale(1.1);
    }
  }
}

// 对话框样式
.tenant-dialog {
  :deep(.el-dialog) {
    border-radius: 16px;
    overflow: hidden;
  }

  :deep(.el-dialog__header) {
    background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
    color: white;
    padding: 20px 24px;
    margin: 0;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
    }

    .el-dialog__headerbtn {
      top: 20px;
      right: 24px;

      .el-dialog__close {
        color: white;
        font-size: 18px;
      }
    }
  }

  :deep(.el-dialog__body) {
    padding: 0;
  }
}

.dialog-content {
  padding: 24px;
}

.tenant-form {
  .form-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid #f1f5f9;
      font-size: 16px;
      font-weight: 600;
      color: #334155;

      .el-icon {
        color: #4f9cf9;
        font-size: 18px;
      }
    }
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #374151;
  }

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }

    &.is-focus {
      box-shadow: 0 0 0 2px rgba(79, 156, 249, 0.2);
    }
  }

  :deep(.el-textarea__inner) {
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }

    &:focus {
      box-shadow: 0 0 0 2px rgba(79, 156, 249, 0.2);
    }
  }

  :deep(.el-select) {
    .el-input__wrapper {
      border-radius: 8px;
    }
  }
}

.dialog-footer {
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .el-button {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;

    &--primary {
      background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
      border: none;

      &:hover {
        opacity: 0.9;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .tenants-container {
    padding: 0;
  }

  .page-header {
    padding: 16px 20px;

    .header-content {
      flex-direction: column;
      gap: 16px;
      align-items: flex-start;
    }

    .header-title {
      .title-icon {
        width: 40px;
        height: 40px;
        font-size: 20px;
      }

      .title-text h1 {
        font-size: 24px;
      }
    }
  }

  .tenants-content {
    padding: 0 20px 20px;
  }

  .tenant-card {
    flex-direction: column;
    gap: 12px;

    .tenant-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }

    .tenant-actions {
      width: 100%;
      justify-content: center;
    }
  }

  .tenant-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
  }
}

// 加载动画
:deep(.el-loading-mask) {
  border-radius: 16px;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner) {
  .el-loading-text {
    color: #4f9cf9;
    font-weight: 500;
  }
}
</style>