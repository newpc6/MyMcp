<template>
  <div class="users-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="page-title">
            <div class="title-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="title-text">
              <h2>用户管理</h2>
              <p class="subtitle">管理系统用户和权限设置</p>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAddUser" class="action-btn primary-btn">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
          <el-button type="success" @click="handleImportUser" class="action-btn success-btn">
            <el-icon><Download /></el-icon>
            导入用户
          </el-button>
        </div>
      </div>
    </div>

    <!-- 用户表格卡片 -->
    <div class="table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          <span>用户列表</span>
        </div>
        <div class="card-extra">
          <span class="user-count">共 {{ users.length }} 个用户</span>
        </div>
      </div>
      
      <div class="card-content">
        <el-table 
          :data="users" 
          v-loading="loading" 
          class="modern-table"
          :header-cell-style="{ background: '#f8fafc', color: '#374151', fontWeight: '600' }"
          :row-style="{ background: '#ffffff' }"
          stripe
        >
          <el-table-column prop="id" label="ID" width="80" align="center">
            <template #default="scope">
              <div class="id-cell">{{ scope.row.id }}</div>
            </template>
          </el-table-column>
          
          <el-table-column prop="username" label="用户名" width="250">
            <template #default="scope">
              <div class="user-info">
                <div class="user-avatar">
                  <el-icon><User /></el-icon>
                </div>
                <span class="username">{{ scope.row.username }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="fullname" label="姓名" width="150">
            <template #default="scope">
              <span class="fullname">{{ scope.row.fullname || '-' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="email" label="邮箱" width="200">
            <template #default="scope">
              <span class="email">{{ scope.row.email || '-' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="管理员" width="100" align="center">
            <template #default="scope">
              <el-tag 
                :type="scope.row.is_admin ? 'danger' : 'info'" 
                class="status-tag admin-tag"
                effect="light"
              >
                {{ scope.row.is_admin ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100" align="center">
            <template #default="scope">
              <el-tag 
                :type="scope.row.status === 'active' ? 'success' : 'warning'" 
                class="status-tag"
                effect="light"
              >
                {{ scope.row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="来源" width="120" align="center">
            <template #default="scope">
              <el-tag 
                v-if="scope.row.platform_type" 
                type="primary" 
                class="platform-tag"
                effect="light"
              >
                {{ getPlatformName(scope.row.platform_type) }}
              </el-tag>
              <el-tag v-else type="info" class="platform-tag" effect="light">本地</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="所属租户" min-width="200">
            <template #default="scope">
              <div class="tenant-tags">
                <el-tag 
                  v-for="tenant in scope.row.tenants" 
                  :key="tenant.id" 
                  type="info" 
                  class="tenant-tag"
                  effect="light"
                >
                  {{ tenant.name }}
                </el-tag>
                <el-tag 
                  v-if="scope.row.tenants.length === 0" 
                  type="danger" 
                  class="tenant-tag"
                  effect="light"
                >
                  无租户
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="280" fixed="right" align="center">
            <template #default="scope">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  type="primary"
                  @click="handleEditUser(scope.row)"
                  :disabled="scope.row.username === 'admin' && currentUser.username !== 'admin'"
                  class="action-btn-small edit-btn"
                  link
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="warning" 
                  @click="handleChangePassword(scope.row)"
                  :disabled="scope.row.username === 'admin' && currentUser.username !== 'admin'"
                  class="action-btn-small password-btn"
                  link
                >
                  <el-icon><Key /></el-icon>
                  修改密码
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="handleDeleteUser(scope.row)"
                  :disabled="scope.row.username === 'admin' || scope.row.id === currentUser.user_id"
                  class="action-btn-small delete-btn"
                  link
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 用户表单对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑用户' : '新增用户'" 
      width="500px"
      class="modern-dialog"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-width="80px" class="modern-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="姓名" prop="fullname">
          <el-input v-model="userForm.fullname" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="管理员" prop="is_admin">
          <el-switch 
            v-model="userForm.is_admin" 
            :disabled="userForm.username === 'admin'"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="isEdit">
          <el-select v-model="userForm.status" style="width: 100%" placeholder="请选择状态">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属租户" prop="tenant_ids">
          <el-select 
            v-model="userForm.tenant_ids" 
            multiple 
            collapse-tags 
            style="width: 100%"
            placeholder="请选择所属租户"
          >
            <el-option v-for="tenant in tenants" :key="tenant.id" :label="tenant.name" :value="tenant.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="saveUser" :loading="saveLoading" class="save-btn">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入用户对话框 -->
    <el-dialog 
      v-model="importDialogVisible" 
      title="导入用户" 
      width="500px"
      class="modern-dialog"
    >
      <el-form ref="importFormRef" :model="importForm" :rules="importRules" label-width="100px" class="modern-form">
        <el-form-item label="平台类型" prop="platform_type">
          <el-select v-model="importForm.platform_type" style="width: 100%" placeholder="请选择平台类型">
            <el-option label="E-GOVA KB" value="egovakb" />
          </el-select>
        </el-form-item>
        <el-form-item label="认证信息" prop="authorization">
          <el-input 
            v-model="importForm.authorization" 
            type="password" 
            show-password 
            placeholder="请输入认证Token" 
          />
        </el-form-item>
        <el-form-item label="所属租户" prop="tenant_ids">
          <el-select 
            v-model="importForm.tenant_ids" 
            multiple 
            collapse-tags 
            style="width: 100%"
            placeholder="请选择所属租户"
          >
            <el-option v-for="tenant in tenants" :key="tenant.id" :label="tenant.name" :value="tenant.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importDialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="importUser" :loading="importLoading" class="save-btn">
            导入
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog 
      v-model="passwordDialogVisible" 
      title="修改密码" 
      width="500px"
      class="modern-dialog"
    >
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px" class="modern-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="passwordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input 
            v-model="passwordForm.password" 
            type="password" 
            show-password 
            placeholder="请输入新密码" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordDialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="savePassword" :loading="passwordLoading" class="save-btn">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import { Plus, Download, User, List, Edit, Key, Delete } from '@element-plus/icons-vue';
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
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 70px);
}

/* 页面头部样式 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  overflow: hidden;
  position: relative;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  pointer-events: none;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  position: relative;
  z-index: 1;
}

.page-title {
  display: flex;
  align-items: center;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.title-icon .el-icon {
  font-size: 24px;
  color: white;
}

.title-text h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.primary-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.primary-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.success-btn {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.success-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* 表格卡片样式 */
.table-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.card-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-title .el-icon {
  font-size: 20px;
  color: #667eea;
}

.card-title span {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
}

.user-count {
  font-size: 14px;
  color: #64748b;
  background: rgba(102, 126, 234, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.card-content {
  padding: 0;
}

/* 表格样式 */
.modern-table {
  border: none;
}

:deep(.el-table) {
  border: none;
  background: transparent;
}

:deep(.el-table__header-wrapper) {
  background: #f8fafc;
}

:deep(.el-table th) {
  background: #f8fafc !important;
  border: none;
  color: #374151;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 12px;
}

:deep(.el-table td) {
  border: none;
  padding: 16px 12px;
  border-bottom: 1px solid #f1f5f9;
}

:deep(.el-table__row) {
  transition: all 0.3s ease;
}

:deep(.el-table__row:hover) {
  background: #f8fafc !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 表格内容样式 */
.id-cell {
  font-weight: 600;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-block;
  min-width: 32px;
  text-align: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.username {
  font-weight: 600;
  color: #1a202c;
}

.fullname, .email {
  color: #64748b;
  font-size: 14px;
}

/* 标签样式 */
.status-tag, .admin-tag, .platform-tag, .tenant-tag {
  border-radius: 20px;
  font-weight: 500;
  font-size: 12px;
  padding: 4px 12px;
  border: none;
}

.tenant-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-btn-small {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
}

.edit-btn {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.edit-btn:hover {
  background: rgba(64, 158, 255, 0.2);
  transform: translateY(-1px);
}

.password-btn {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.password-btn:hover {
  background: rgba(230, 162, 60, 0.2);
  transform: translateY(-1px);
}

.delete-btn {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.delete-btn:hover {
  background: rgba(245, 108, 108, 0.2);
  transform: translateY(-1px);
}

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  margin: 0;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__headerbtn) {
  top: 24px;
  right: 24px;
}

:deep(.el-dialog__close) {
  color: white;
  font-size: 18px;
}

:deep(.el-dialog__body) {
  padding: 32px;
  background: white;
}

:deep(.el-dialog__footer) {
  padding: 24px 32px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

/* 表单样式 */
.modern-form {
  margin: 0;
}

:deep(.el-form-item__label) {
  color: #374151;
  font-weight: 600;
  font-size: 14px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

:deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
}

:deep(.el-switch) {
  --el-switch-on-color: #667eea;
}

/* 对话框底部按钮 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  padding: 10px 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.save-btn {
  padding: 10px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .users-container {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
  
  .action-btn {
    flex: 1;
    max-width: 150px;
  }
}

/* 加载动画 */
:deep(.el-loading-mask) {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner) {
  color: #667eea;
}

/* 滚动条样式 */
:deep(.el-table__body-wrapper)::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

:deep(.el-table__body-wrapper)::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

:deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

:deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>