<template>
  <aside class="sidebar-container">
    <div class="brand-logo" @click="goToHome">
      <div class="brand-icon">
        <el-icon>
          <Connection />
        </el-icon>
      </div>
      <div class="brand-text">
        <span class="brand-name">MCP</span>
        <span class="brand-subtitle">管理平台</span>
      </div>
    </div>

    <el-menu router :default-active="$route.path" class="nav-menu">
      <el-menu-item index="/marketplace" @mouseup="handleMouseUp($event, '/marketplace')">
        <el-icon><Collection /></el-icon>
        <span>MCP模板广场</span>
      </el-menu-item>
      <el-menu-item index="/server" @mouseup="handleMouseUp($event, '/server')">
        <el-icon><Monitor /></el-icon>
        <span>MCP服务管理</span>
      </el-menu-item>
      <el-menu-item v-if="isAdmin" index="/statistics" @mouseup="handleMouseUp($event, '/statistics')">
        <el-icon><DataAnalysis /></el-icon>
        <span>统计分析</span>
      </el-menu-item>
      <el-menu-item v-if="isAdmin" index="/users" @mouseup="handleMouseUp($event, '/users')">
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </el-menu-item>
      <el-menu-item v-if="isAdmin" index="/tenants" @mouseup="handleMouseUp($event, '/tenants')">
        <el-icon><OfficeBuilding /></el-icon>
        <span>租户管理</span>
      </el-menu-item>
      <el-menu-item v-if="isAdmin" index="/system" @mouseup="handleMouseUp($event, '/system')">
        <el-icon><Setting /></el-icon>
        <span>系统管理</span>
      </el-menu-item>
    </el-menu>

    <div class="sidebar-footer">
      <el-dropdown v-if="isLoggedIn" trigger="click" @command="handleCommand">
        <button class="user-dropdown-link" type="button">
          <span class="user-avatar">{{ userInitial }}</span>
          <span class="user-name">{{ userInfo.username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="change-password">修改密码</el-dropdown-item>
            <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <el-button v-else type="primary" class="login-button" @click="handleLogin">登录</el-button>
    </div>

    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePassword" :loading="changing">
          确定
        </el-button>
      </template>
    </el-dialog>
  </aside>
</template>
<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import type { FormInstance } from 'element-plus';
import {
  ArrowDown,
  Collection,
  Connection,
  DataAnalysis,
  Monitor,
  OfficeBuilding,
  Setting,
  User
} from '@element-plus/icons-vue';
import { logout, changePassword as apiChangePassword } from '@/api/auth';

defineOptions({
  name: 'NavbarComponent'
});

const router = useRouter();
const passwordDialogVisible = ref(false);
const changing = ref(false);
const passwordFormRef = ref<FormInstance>();

// 获取用户信息
const userInfo = reactive<any>({
  username: '',
  user_id: null,
  is_admin: false
});

// 计算属性
const isLoggedIn = computed(() => !!userInfo.user_id);
const isAdmin = computed(() => userInfo.is_admin);
const userInitial = computed(() => (userInfo.username || 'U').slice(0, 1).toUpperCase());

// 初始化用户信息
try {
  const userInfoStr = localStorage.getItem('userInfo');
  if (userInfoStr) {
    const parsed = JSON.parse(userInfoStr);
    userInfo.username = parsed.username;
    userInfo.user_id = parsed.user_id;
    userInfo.is_admin = parsed.is_admin;
  }
} catch (error) {
  console.error('获取用户信息失败', error);
}

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 密码验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

const handleMouseUp = (event: MouseEvent, path: string) => {
  // 鼠标中键点击 (button === 1)
  if (event.button === 1) {
    event.preventDefault();
    // 在新标签页打开链接
    window.open(path, '_blank');
  }
};

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await logout();
      ElMessage.success('退出登录成功');
    } catch (error) {
      console.error('登出API调用失败', error);
    } finally {
      // 清除本地用户信息并跳转到登录页
      localStorage.removeItem('userInfo');
      router.push('/login');
    }
  } else if (command === 'change-password') {
    passwordForm.oldPassword = '';
    passwordForm.newPassword = '';
    passwordForm.confirmPassword = '';
    passwordDialogVisible.value = true;
  }
};

// 处理登录按钮点击
const handleLogin = () => {
  router.push('/login');
};

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return;

  try {
    await passwordFormRef.value.validate();

    changing.value = true;

    const response = await apiChangePassword(
      passwordForm.oldPassword,
      passwordForm.newPassword
    );

    if (response.data.code === 0) {
      ElMessage.success('密码修改成功');
      passwordDialogVisible.value = false;
    } else {
      ElMessage.error(response.data.message || '密码修改失败');
    }
  } catch (error: any) {
    if (error.response) {
      ElMessage.error(error.response.data.message || '密码修改失败');
    } else if (error.message) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error('密码修改失败');
    }
  } finally {
    changing.value = false;
  }
};

// 点击logo回到首页
const goToHome = () => {
  router.push('/');
};
</script>

<style scoped>
.sidebar-container {
  width: 232px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--common-text-color-positive);
  background-image: var(--menu-background-image);
  box-shadow: 4px 4px 40px 0 var(--header-shadow-color);
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 52px;
  padding: 0 16px;
  cursor: pointer;
  border-bottom: 1px solid var(--menu-border-color);
}

.brand-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--menu-panel-background-color);
  border: 1px solid var(--menu-border-color);
  color: var(--common-text-color-positive);
  flex: 0 0 auto;
}

.brand-icon .el-icon {
  font-size: 18px;
}

.brand-text {
  min-width: 0;
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-name {
  color: var(--common-text-color-positive);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0;
}

.brand-subtitle {
  margin-top: 3px;
  color: var(--menu-text-color-light);
  font-size: 12px;
}

.nav-menu {
  flex: 1;
  padding: 8px;
  border-right: 0;
  background: transparent;
}

.nav-menu :deep(.el-menu-item) {
  height: 40px;
  margin: 2px 0;
  padding: 0 14px !important;
  border-radius: var(--common-radius-sm);
  color: var(--menu-text-color);
  line-height: 40px;
  transition: background 0.2s ease, color 0.2s ease;
}

.nav-menu :deep(.el-menu-item .el-icon) {
  color: inherit;
  font-size: 16px;
}

.nav-menu :deep(.el-menu-item:hover) {
  background: var(--menu-hover-background-color);
  color: var(--common-text-color-positive);
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: var(--common-primary-color);
  color: var(--common-text-color-positive);
  font-weight: 600;
  box-shadow: none;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--menu-border-color);
}

.user-dropdown-link {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 10px;
  color: var(--common-text-color-positive);
  background: var(--menu-panel-background-color);
  border: 1px solid var(--menu-border-color);
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.user-dropdown-link:hover {
  background: var(--menu-panel-background-color-hover);
}

.user-avatar {
  width: 26px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--common-text-color-positive);
  color: var(--common-primary-color);
  font-size: 12px;
  font-weight: 700;
}

.user-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.login-button {
  width: 100%;
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  padding: 18px 20px;
  border-bottom: 1px solid var(--common-border-color);
  margin-right: 0;
}

:deep(.el-dialog__title) {
  color: var(--common-text-color-heavy);
  font-weight: 600;
}

:deep(.el-form-item__label) {
  color: var(--common-text-color);
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
}
</style>
