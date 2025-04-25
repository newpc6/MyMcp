<template>
  <div class="tenants-container">
    <div class="tenants-header">
      <h2>租户管理</h2>
      <el-button type="primary" @click="handleAddTenant">
        <el-icon><Plus /></el-icon> 新增租户
      </el-button>
    </div>
    
    <el-table 
      :data="tenants" 
      v-loading="loading"
      border 
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="租户名称" width="180" />
      <el-table-column prop="code" label="租户代码" width="180" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'warning'">
            {{ scope.row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button 
            size="small" 
            @click="handleEditTenant(scope.row)"
            :disabled="scope.row.code === 'default'"
          >
            编辑
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDeleteTenant(scope.row)"
            :disabled="scope.row.code === 'default'"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 租户表单对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑租户' : '新增租户'"
      width="500px"
    >
      <el-form 
        ref="tenantFormRef" 
        :model="tenantForm" 
        :rules="tenantRules" 
        label-width="80px"
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
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { 
  getAllTenants, 
  createTenant, 
  updateTenant, 
  deleteTenant
} from '@/api/auth';

// 状态
const loading = ref(false);
const tenants = ref<any[]>([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const saveLoading = ref(false);

// 租户表单
const tenantFormRef = ref<FormInstance>();
const tenantForm = reactive({
  id: null as number | null,
  name: '',
  code: '',
  description: '',
  status: 'active'
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

// 初始化
onMounted(async () => {
  await fetchTenants();
});

// 获取所有租户
const fetchTenants = async () => {
  loading.value = true;
  try {
    const data = await getAllTenants();
    tenants.value = data.data;
  } catch (error: any) {
    ElMessage.error('获取租户列表失败: ' + (error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
};

// 新增租户
const handleAddTenant = () => {
  isEdit.value = false;
  tenantForm.id = null;
  tenantForm.name = '';
  tenantForm.code = '';
  tenantForm.description = '';
  tenantForm.status = 'active';
  dialogVisible.value = true;
};

// 编辑租户
const handleEditTenant = (row: any) => {
  isEdit.value = true;
  tenantForm.id = row.id;
  tenantForm.name = row.name;
  tenantForm.code = row.code;
  tenantForm.description = row.description || '';
  tenantForm.status = row.status;
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
      description: tenantForm.description
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
</style> 