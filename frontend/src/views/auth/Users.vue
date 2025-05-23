<template>
  <div class="users-container">
    <div class="users-header">
      <h2>用户管理</h2>
      <div>
        <el-button type="primary" @click="handleAddUser" style="margin-right: 10px;">
          <el-icon>
            <Plus />
          </el-icon> 新增用户
        </el-button>
        <el-button type="success" @click="handleImportUser">
          <el-icon>
            <Download />
          </el-icon> 导入用户
        </el-button>
      </div>
    </div>

    <el-table :data="users" v-loading="loading" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="fullname" label="姓名" width="150" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column label="管理员" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_admin ? 'danger' : 'info'">
            {{ scope.row.is_admin ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'warning'">
            {{ scope.row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="120">
        <template #default="scope">
          <el-tag v-if="scope.row.platform_type" type="primary">
            {{ getPlatformName(scope.row.platform_type) }}
          </el-tag>
          <el-tag v-else type="info">本地</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="所属租户" min-width="200">
        <template #default="scope">
          <el-space wrap>
            <el-tag v-for="tenant in scope.row.tenants" :key="tenant.id" type="info">
              {{ tenant.name }}
            </el-tag>
            <el-tag v-if="scope.row.tenants.length === 0" type="danger">无租户</el-tag>
          </el-space>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="handleEditUser(scope.row)"
            :disabled="scope.row.username === 'admin' && currentUser.username !== 'admin'">
            编辑
          </el-button>
          <el-button size="small" type="warning" @click="handleChangePassword(scope.row)"
            :disabled="scope.row.username === 'admin' && currentUser.username !== 'admin'">
            修改密码
          </el-button>
          <el-button size="small" type="danger" @click="handleDeleteUser(scope.row)"
            :disabled="scope.row.username === 'admin' || scope.row.id === currentUser.user_id">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 用户表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="fullname">
          <el-input v-model="userForm.fullname" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="管理员" prop="is_admin">
          <el-switch v-model="userForm.is_admin" :disabled="userForm.username === 'admin'" />
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="isEdit">
          <el-select v-model="userForm.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属租户" prop="tenant_ids">
          <el-select v-model="userForm.tenant_ids" multiple collapse-tags style="width: 100%">
            <el-option v-for="tenant in tenants" :key="tenant.id" :label="tenant.name" :value="tenant.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入用户对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入用户" width="500px">
      <el-form ref="importFormRef" :model="importForm" :rules="importRules" label-width="100px">
        <el-form-item label="平台类型" prop="platform_type">
          <el-select v-model="importForm.platform_type" style="width: 100%">
            <el-option label="E-GOVA KB" value="egovakb" />
          </el-select>
        </el-form-item>
        <el-form-item label="认证信息" prop="authorization">
          <el-input v-model="importForm.authorization" type="password" show-password placeholder="请输入认证Token" />
        </el-form-item>
        <el-form-item label="所属租户" prop="tenant_ids">
          <el-select v-model="importForm.tenant_ids" multiple collapse-tags style="width: 100%">
            <el-option v-for="tenant in tenants" :key="tenant.id" :label="tenant.name" :value="tenant.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="importUser" :loading="importLoading">
          导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="500px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="passwordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="passwordForm.password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePassword" :loading="passwordLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import { Plus, Download } from '@element-plus/icons-vue';
import {
  getAllUsers,
  createUser,
  updateUser,
  deleteUser,
  getAllTenants,
  importPlatformUser
} from '@/api/auth';

// 状态
const loading = ref(false);
const users = ref<any[]>([]);
const tenants = ref<any[]>([]);
const dialogVisible = ref(false);
const importDialogVisible = ref(false);
const passwordDialogVisible = ref(false);
const isEdit = ref(false);
const saveLoading = ref(false);
const importLoading = ref(false);
const passwordLoading = ref(false);
const currentUser = reactive<any>({
  user_id: null,
  username: '',
  is_admin: false
});

// 获取用户信息
try {
  const userInfo = localStorage.getItem('userInfo');
  if (userInfo) {
    const parsedInfo = JSON.parse(userInfo);
    currentUser.user_id = parsedInfo.user_id;
    currentUser.username = parsedInfo.username;
    currentUser.is_admin = parsedInfo.is_admin;
  }
} catch (error) {
  console.error('获取用户信息失败', error);
}

// 用户表单
const userFormRef = ref<FormInstance>();
const userForm = reactive({
  id: null as number | null,
  username: '',
  password: '',
  fullname: '',
  email: '',
  is_admin: false,
  status: 'active',
  tenant_ids: [] as number[]
});

// 密码修改表单
const passwordFormRef = ref<FormInstance>();
const passwordForm = reactive({
  id: null as number | null,
  username: '',
  password: ''
});

// 导入表单
const importFormRef = ref<FormInstance>();
const importForm = reactive({
  platform_type: 'egovakb',
  authorization: '',
  tenant_ids: [] as number[]
});

// 验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
  ],
  email: [
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (!value) {
          callback(); // 邮箱可以为空
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          callback(new Error('请输入正确的邮箱地址'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

// 密码修改验证规则
const passwordRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
  ]
};

// 导入验证规则
const importRules = {
  platform_type: [
    { required: true, message: '请选择平台类型', trigger: 'change' }
  ],
  authorization: [
    { required: true, message: '请输入认证信息', trigger: 'blur' }
  ]
};

// 初始化
onMounted(async () => {
  await Promise.all([fetchUsers(), fetchTenants()]);
});

// 获取所有用户
const fetchUsers = async () => {
  loading.value = true;
  try {
    const data = await getAllUsers();
    console.log(data);
    users.value = data.data;
  } catch (error: any) {
    ElMessage.error('获取用户列表失败: ' + (error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
};

// 获取所有租户
const fetchTenants = async () => {
  try {
    const data = await getAllTenants();
    tenants.value = data.data;
  } catch (error) {
    ElMessage.error('获取租户列表失败');
  }
};

// 获取平台名称
const getPlatformName = (type: string) => {
  const platformMap: Record<string, string> = {
    'egovakb': 'E-GOVA KB'
  };
  return platformMap[type] || type;
};

// 新增用户
const handleAddUser = () => {
  isEdit.value = false;
  userForm.id = null;
  userForm.username = '';
  userForm.password = '';
  userForm.fullname = '';
  userForm.email = '';
  userForm.is_admin = false;
  userForm.status = 'active';
  userForm.tenant_ids = [];
  dialogVisible.value = true;
};

// 编辑用户
const handleEditUser = (row: any) => {
  isEdit.value = true;
  userForm.id = row.id;
  userForm.username = row.username;
  userForm.password = ''; // 编辑时不关心密码
  userForm.fullname = row.fullname || '';
  userForm.email = row.email || '';
  userForm.is_admin = row.is_admin;
  userForm.status = row.status;
  // 设置用户所属租户
  userForm.tenant_ids = row.tenants.map((t: any) => t.id);
  dialogVisible.value = true;
};

// 修改密码
const handleChangePassword = (row: any) => {
  passwordForm.id = row.id;
  passwordForm.username = row.username;
  passwordForm.password = '';
  passwordDialogVisible.value = true;
};

// 删除用户
const handleDeleteUser = (row: any) => {
  ElMessageBox.confirm(
    `确定删除用户 ${row.username} 吗？此操作不可撤销！`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const data = await deleteUser(row.id);
      if (data.code === 0 || data.code === 200) {
        ElMessage.success('删除成功');
        await fetchUsers();
      } else {
        ElMessage.error(data.message || '删除失败');
      }
    } catch (error: any) {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'));
    }
  }).catch(() => { });
};

// 保存用户
const saveUser = async () => {
  if (!userFormRef.value) return;

  try {
    // 打印表单内容以便调试
    console.log('Form data before validation:', JSON.stringify(userForm));
    console.log('Is edit mode:', isEdit.value);
    
    await userFormRef.value.validate();
    
    saveLoading.value = true;

    // 准备提交的数据
    const userData: any = {
      username: userForm.username,
      fullname: userForm.fullname,
      email: userForm.email,
      is_admin: userForm.is_admin,
      tenant_ids: userForm.tenant_ids
    };

    // 如果是新建用户，则需要密码
    if (!isEdit.value) {
      userData.password = userForm.password;
    }

    // 如果是编辑模式，则加入状态字段
    if (isEdit.value) {
      userData.status = userForm.status;
    }

    console.log('User data to submit:', JSON.stringify(userData));

    let data;
    if (isEdit.value) {
      console.log(`Updating user with ID: ${userForm.id}`);
      data = await updateUser(userForm.id!, userData);
      console.log('Update response:', data);
    } else {
      console.log('Creating new user');
      data = await createUser(userData);
      console.log('Create response:', data);
    }

    if (data.code === 0 || data.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
      dialogVisible.value = false;
      await fetchUsers();
    } else {
      ElMessage.error(data.message || (isEdit.value ? '更新失败' : '创建失败'));
      console.error('API返回错误:', data);
    }
  } catch (error: any) {
    console.error('操作失败:', error);
    if (error.response) {
      console.error('Response error:', error.response);
      ElMessage.error(error.response.data?.error || '操作失败');
    } else {
      ElMessage.error('操作失败: ' + (error.message || '未知错误'));
    }
  } finally {
    saveLoading.value = false;
  }
};

// 保存密码
const savePassword = async () => {
  if (!passwordFormRef.value) return;
  
  try {
    await passwordFormRef.value.validate();
    
    passwordLoading.value = true;
    
    // 准备提交的数据
    const userData = {
      password: passwordForm.password
    };
    
    console.log(`Updating password for user ID: ${passwordForm.id}`);
    const data = await updateUser(passwordForm.id!, userData);
    console.log('Update password response:', data);
    
    if (data.code === 0 || data.code === 200) {
      ElMessage.success('密码修改成功');
      passwordDialogVisible.value = false;
    } else {
      ElMessage.error(data.message || '密码修改失败');
      console.error('API返回错误:', data);
    }
  } catch (error: any) {
    console.error('密码修改失败:', error);
    if (error.response) {
      console.error('Response error:', error.response);
      ElMessage.error(error.response.data?.error || '密码修改失败');
    } else {
      ElMessage.error('密码修改失败: ' + (error.message || '未知错误'));
    }
  } finally {
    passwordLoading.value = false;
  }
};

// 导入用户
const handleImportUser = () => {
  importForm.platform_type = 'egovakb';
  importForm.authorization = '';
  importForm.tenant_ids = [];
  importDialogVisible.value = true;
};

// 执行导入
const importUser = async () => {
  if (!importFormRef.value) return;

  try {
    await importFormRef.value.validate();

    importLoading.value = true;

    const data = await importPlatformUser({
      platform_type: importForm.platform_type,
      authorization: importForm.authorization,
      tenant_ids: importForm.tenant_ids
    });

    if (data.code === 0 || data.code === 200) {
      ElMessage.success(data.message || '导入成功');
      importDialogVisible.value = false;
      await fetchUsers();
    } else {
      ElMessage.error(data.message || '导入失败');
    }
  } catch (error: any) {
    if (error.response) {
      ElMessage.error(error.response.data.error || '导入失败');
    } else {
      ElMessage.error('导入失败: ' + (error.message || '未知错误'));
    }
  } finally {
    importLoading.value = false;
  }
};
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.users-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}
</style>