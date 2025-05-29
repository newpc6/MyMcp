<template>
  <div class="navbar-container">
    <el-menu mode="horizontal" router :ellipsis="false" class="nav-menu">
      <div class="flex-grow logo-container">
        <h1 class="text-xl font-bold text-primary">MCP管理平台</h1>
      </div>

      <!-- <el-menu-item index="/" @mouseup="handleMouseUp($event, '/')">首页</el-menu-item> -->
      <el-menu-item index="/marketplace" @mouseup="handleMouseUp($event, '/marketplace')">MCP广场</el-menu-item>
      <el-menu-item index="/mcp-services" @mouseup="handleMouseUp($event, '/mcp-services')">MCP服务管理</el-menu-item>
      <el-menu-item v-if="isAdmin" index="/statistics"
        @mouseup="handleMouseUp($event, '/statistics')">统计分析</el-menu-item>
      <el-menu-item v-if="isAdmin" index="/users" @mouseup="handleMouseUp($event, '/users')">用户管理</el-menu-item>
      <el-menu-item v-if="isAdmin" index="/tenants" @mouseup="handleMouseUp($event, '/tenants')">租户管理</el-menu-item>

      <div class="user-controls">
        <el-dropdown v-if="isLoggedIn" @command="handleCommand">
          <span class="user-dropdown-link">
            {{ userInfo.username }} <el-icon>
              <ArrowDown />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="change-password">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button v-else type="primary" size="small" @click="handleLogin">登录</el-button>
      </div>

      <!-- <div class="version-info">
        <span class="text-sm">版本: v1.0.0</span>
      </div> -->
    </el-menu>

    <!-- 修改密码对话框 -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';
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
</script>

<style scoped>
.navbar-container {
  border-bottom: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
  position: relative;
}

.navbar-container::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
}

.nav-menu {
  display: flex;
  align-items: center;
  height: 70px;
  padding: 0 30px;
  background: transparent;
}

.flex-grow {
  flex-grow: 1;
}

.logo-container {
  display: flex;
  align-items: center;
  padding-right: 30px;
}

.logo-container h1 {
  color: white !important;
  font-size: 24px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin: 0;
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.text-primary {
  color: white !important;
}

.version-info {
  display: flex;
  align-items: center;
  padding: 0 20px;
  color: rgba(255, 255, 255, 0.8);
}

.user-controls {
  display: flex;
  align-items: center;
  margin-left: 30px;
}

.user-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.user-dropdown-link:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-controls .el-button {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 500;
  border-radius: 20px;
  padding: 8px 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.user-controls .el-button:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-menu-item) {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  margin: 0 4px;
  padding: 0 16px;
  height: 40px;
  line-height: 40px;
  transition: all 0.3s ease;
  background: transparent;
  border-bottom: none;
}

:deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-menu--horizontal) {
  border-bottom: none;
  background: transparent;
}

:deep(.el-menu--horizontal .el-menu-item:not(.is-disabled):focus) {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

/* 对话框样式优化 */
:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

:deep(.el-form-item__label) {
  color: #374151;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}
</style>