<template>
  <aside class="sidebar-container">
    <el-menu router :default-active="$route.path" class="nav-menu">
      <el-menu-item index="/marketplace" @mouseup="handleMouseUp($event, '/marketplace')">
        <span class="menu-icon-box is-soft">
          <el-icon><Collection /></el-icon>
        </span>
        <span class="text">MCP模板广场</span>
      </el-menu-item>

      <el-sub-menu index="mcp-manage">
        <template #title>
          <span class="menu-icon-box is-soft">
            <el-icon><Monitor /></el-icon>
          </span>
          <span class="text">MCP管理</span>
        </template>
        <el-menu-item index="/server" @mouseup="handleMouseUp($event, '/server')">
          <span class="menu-icon-box is-soft">
            <el-icon><Grid /></el-icon>
          </span>
          <span class="text">服务管理</span>
        </el-menu-item>
        <el-menu-item index="/mcp-auth/secret-management" @mouseup="handleMouseUp($event, '/mcp-auth/secret-management')">
          <span class="menu-icon-box is-soft">
            <el-icon><Key /></el-icon>
          </span>
          <span class="text">密钥管理</span>
        </el-menu-item>
        <el-menu-item index="/mcp-auth/access-logs" @mouseup="handleMouseUp($event, '/mcp-auth/access-logs')">
          <span class="menu-icon-box is-soft">
            <el-icon><Document /></el-icon>
          </span>
          <span class="text">访问日志</span>
        </el-menu-item>
      </el-sub-menu>

      <el-sub-menu v-if="isAdmin" index="ops-manage">
        <template #title>
          <span class="menu-icon-box is-soft">
            <el-icon><Setting /></el-icon>
          </span>
          <span class="text">运维管理</span>
        </template>
        <el-menu-item index="/system" @mouseup="handleMouseUp($event, '/system')">
          <span class="menu-icon-box is-soft">
            <el-icon><Setting /></el-icon>
          </span>
          <span class="text">系统管理</span>
        </el-menu-item>
        <el-menu-item index="/statistics" @mouseup="handleMouseUp($event, '/statistics')">
          <span class="menu-icon-box is-soft">
            <el-icon><DataAnalysis /></el-icon>
          </span>
          <span class="text">统计分析</span>
        </el-menu-item>
      </el-sub-menu>

      <el-sub-menu v-if="isAdmin" index="permission-manage">
        <template #title>
          <span class="menu-icon-box is-soft">
            <el-icon><Lock /></el-icon>
          </span>
          <span class="text">权限管理</span>
        </template>
        <el-menu-item index="/users" @mouseup="handleMouseUp($event, '/users')">
          <span class="menu-icon-box is-soft">
            <el-icon><User /></el-icon>
          </span>
          <span class="text">用户管理</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>

    <div class="collapse-trigger">
      <el-icon><Fold /></el-icon>
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
        <el-button type="primary" :loading="changing" @click="changePassword">
          确定
        </el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from 'vue';
import { ElMessage } from 'element-plus';
import type { FormInstance } from 'element-plus';
import {
  Collection,
  DataAnalysis,
  Document,
  Fold,
  Grid,
  Key,
  Lock,
  Monitor,
  Setting,
  User
} from '@element-plus/icons-vue';
import { changePassword as apiChangePassword } from '@/api/auth';

defineOptions({
  name: 'NavbarComponent'
});

const passwordDialogVisible = ref(false);
const changing = ref(false);
const passwordFormRef = ref<FormInstance>();

const userInfo = reactive<any>({
  username: '',
  user_id: null,
  is_admin: false
});

const isAdmin = computed(() => userInfo.is_admin);

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

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

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
  if (event.button === 1) {
    event.preventDefault();
    window.open(path, '_blank');
  }
};

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
.sidebar-container {
  width: 220px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: var(--common-text-color);
  background: var(--menu-background-color);
}

.nav-menu {
  --el-menu-bg-color: var(--menu-background-color);
  --el-menu-text-color: var(--common-text-color);
  --el-menu-active-color: var(--common-primary-color);
  --el-menu-hover-bg-color: var(--common-hover-background-color);

  flex: 1;
  overflow-y: auto;
  border-right: 0;
  background: var(--menu-background-color);
}

.nav-menu :deep(.el-menu),
.nav-menu :deep(.el-sub-menu),
.nav-menu :deep(.el-menu--inline) {
  background: var(--menu-background-color);
}

.nav-menu :deep(.el-menu-item),
.nav-menu :deep(.el-sub-menu__title) {
  height: 44px;
  display: flex;
  align-items: center;
  margin: 4px 8px;
  padding: 0 14px !important;
  color: var(--common-text-color);
  border-radius: var(--common-radius-md);
  font-size: var(--common-font-size-base);
  line-height: 44px;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.nav-menu :deep(.el-menu--inline .el-menu-item) {
  padding-left: 34px !important;
}

.nav-menu :deep(.el-sub-menu__icon-arrow) {
  right: 16px;
  margin-top: -6px;
  color: var(--common-text-color-light);
  font-size: 12px;
}

.nav-menu :deep(.el-menu-item:hover),
.nav-menu :deep(.el-sub-menu__title:hover),
.nav-menu :deep(.el-menu-item.is-active) {
  color: var(--common-primary-color);
  background: var(--common-hover-background-color);
}

.nav-menu :deep(.el-menu-item.is-active) {
  font-weight: 600;
}

.nav-menu :deep(.el-menu-item.is-active .menu-icon-box),
.nav-menu :deep(.el-sub-menu.is-active > .el-sub-menu__title .menu-icon-box) {
  color: var(--common-on-primary-color);
  background: var(--common-primary-color);
}

.menu-icon-box {
  width: 26px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 8px;
  color: var(--common-primary-color);
  border-radius: var(--common-radius-md);
}

.menu-icon-box.is-soft {
  background: var(--zartd-primary-1);
  box-shadow: var(--common-shadow-xs);
}

.menu-icon-box .el-icon {
  margin-right: 0;
  font-size: 16px;
}

.text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.collapse-trigger {
  height: 40px;
  flex: 0 0 40px;
  color: var(--common-text-color);
  text-align: center;
  border-top: 1px solid var(--common-border-color);
  background: var(--common-surface-color);
  cursor: pointer;
  font-size: 18px;
  line-height: 40px;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.collapse-trigger:hover {
  color: var(--common-primary-color);
  background: var(--common-hover-background-color);
}

:deep(.el-dialog) {
  border-radius: var(--common-radius-lg);
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
</style>
