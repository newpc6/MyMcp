<template>
  <div class="tenants-container">
    <div class="tenants-header">
      <h2>租户管理</h2>
      <el-button type="primary" @click="handleAddTenant">
        <el-icon><Plus /></el-icon> 新增租户
      </el-button>
    </div>
    
    <el-tree
      v-loading="loading"
      :data="tenantTree"
      node-key="id"
      default-expand-all
      :props="defaultProps"
      class="tenant-tree"
    >
      <template #default="{ data }">
        <div class="tenant-node">
          <div class="tenant-info">
            <div class="tenant-basic">
              <span class="tenant-name">{{ data.name }}</span>
              <span class="tenant-code">({{ data.code }})</span>
              <el-tag size="small" :type="data.status === 'active' ? 'success' : 'warning'" class="tenant-status">
                {{ data.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </div>
            <div class="tenant-detail">
              <el-text v-if="data.description" type="info" size="small" class="tenant-description">
                {{ data.description }}
              </el-text>
            </div>
          </div>
          <div class="tenant-actions">
            <el-button 
              size="small" 
              @click.stop="handleAddSubTenant(data)"
              type="success"
              plain
            >
              <el-icon><Plus /></el-icon> 添加子租户
            </el-button>
            <el-button 
              size="small" 
              @click.stop="handleEditTenant(data)"
              :disabled="data.code === 'default'"
              type="primary"
              plain
            >
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click.stop="handleDeleteTenant(data)"
              :disabled="data.code === 'default'"
              plain
            >
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </div>
      </template>
    </el-tree>
    
    <!-- 租户表单对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑租户' : (isSubTenant ? '新增子租户' : '新增租户')"
      width="500px"
    >
      <el-form 
        ref="tenantFormRef" 
        :model="tenantForm" 
        :rules="tenantRules" 
        label-width="100px"
      >
        <el-form-item label="租户名称" prop="name">
          <el-input v-model="tenantForm.name" />
        </el-form-item>
        <el-form-item label="租户代码" prop="code" v-if="!isEdit">
          <el-input v-model="tenantForm.code" />
        </el-form-item>
        <el-form-item label="租户代码" v-else>
          <el-input v-model="tenantForm.code" disabled />
        </el-form-item>
        <el-form-item label="上级租户" v-if="!isEdit">
          <el-select v-model="tenantForm.parent_id" clearable style="width: 100%">
            <el-option label="无上级租户" :value="null" />
            <el-option 
              v-for="tenant in flattenedTenants" 
              :key="tenant.id" 
              :label="tenant.name" 
              :value="tenant.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="上级租户" v-else>
          <el-select v-model="tenantForm.parent_id" clearable style="width: 100%" :disabled="tenantForm.code === 'default'">
            <el-option label="无上级租户" :value="null" />
            <el-option 
              v-for="tenant in flattenedTenants.filter(t => t.id !== tenantForm.id)" 
              :key="tenant.id" 
              :label="tenant.name" 
              :value="tenant.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="tenantForm.description" 
            type="textarea" 
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="isEdit">
          <el-select v-model="tenantForm.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTenant" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import { Plus, Edit, Delete } from '@element-plus/icons-vue';
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
  }).catch(() => {});
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

<style scoped>
.tenants-container {
  padding: 20px;
}

.tenants-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tenants-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.tenant-tree {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.tenant-tree :deep(.el-tree-node__content) {
  height: auto;
  padding: 8px 0;
}

.tenant-tree :deep(.el-tree-node:hover .tenant-node) {
  background-color: #f0f9ff;
  transition: background-color 0.3s;
  border-radius: 6px;
}

.tenant-node {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 6px;
  transition: all 0.3s;
  position: relative;
  border-left: 3px solid transparent;
}

.tenant-node:hover {
  border-left-color: var(--el-color-primary);
}

.tenant-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 70%;
}

.tenant-basic {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.tenant-name {
  font-weight: bold;
  color: #303133;
  font-size: 16px;
}

.tenant-code {
  color: #606266;
  font-size: 14px;
}

.tenant-detail {
  margin-top: 3px;
}

.tenant-description {
  display: inline-block;
  color: #909399;
  font-size: 13px;
  line-height: 1.4;
  margin-top: 2px;
  word-break: break-word;
}

.tenant-status {
  margin-left: 6px;
}

.tenant-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

@media (max-width: 768px) {
  .tenant-node {
    flex-direction: column;
    gap: 10px;
  }
  
  .tenant-info {
    max-width: 100%;
  }
  
  .tenant-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style> 