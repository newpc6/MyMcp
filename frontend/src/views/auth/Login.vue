<template>
  <div class="login-container">
    <div class="background-decoration">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <div class="login-box">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="48" color="#4f9cf9">
            <Platform />
          </el-icon>
        </div>
        <h2>MCP管理平台</h2>
        <p>欢迎回来，请登录您的账号</p>
      </div>

      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top" class="login-form"
        size="large">
        <el-form-item prop="username" label="用户名">
          <el-input v-model="loginForm.username" prefix-icon="User" placeholder="请输入用户名" class="form-input" />
        </el-form-item>

        <el-form-item prop="password" label="密码">
          <el-input v-model="loginForm.password" prefix-icon="Lock" :type="passwordVisible ? 'text' : 'password'"
            placeholder="请输入密码" class="form-input" @keyup.enter="handleLogin">
            <template #suffix>
              <el-icon class="password-icon" @click="passwordVisible = !passwordVisible">
                <component :is="passwordVisible ? 'View' : 'Hide'" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" class="login-button" size="large" @click="handleLogin">
            <span v-if="!loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-tips" v-if="errorMessage">
        <el-alert :title="errorMessage" type="error" show-icon :closable="false" />
      </div>

      <div class="login-footer">
        <p>© 2025 MCP管理平台 - 现代化微服务管理系统</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance } from 'element-plus';
import { login } from '@/api/auth';
import { View, Hide, Platform } from '@element-plus/icons-vue';

// 路由
const router = useRouter();

// 表单引用
const loginForm = reactive({
  username: '',
  password: ''
});
const loginFormRef = ref<FormInstance>();
const passwordVisible = ref(false);

// 验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
};

// 状态
const loading = ref(false);
const errorMessage = ref('');

// 登录方法
const handleLogin = async () => {
  if (!loginFormRef.value) return;

  try {
    // 表单验证
    await loginFormRef.value.validate();

    // 开始登录
    loading.value = true;
    errorMessage.value = '';

    const data = await login(loginForm.username, loginForm.password);
    console.log('登录响应:', data);

    if (data.code === 0) {
      // 确认响应中包含必要数据
      const userData = data.data;
      if (!userData || !userData.token) {
        errorMessage.value = '服务器返回的用户数据不完整';
        console.error('登录响应中缺少token', userData);
        return;
      }

      // 输出token前15个字符用于调试
      console.log('获取到token(前15个字符):', userData.token.substring(0, 15));

      // 存储用户信息到本地存储
      localStorage.setItem('userInfo', JSON.stringify(userData));
      console.log('保存用户信息到localStorage完成');

      // 确认是否成功保存，读取回来验证
      const savedUserInfo = localStorage.getItem('userInfo');
      console.log('验证保存结果:', savedUserInfo ? '保存成功' : '保存失败');

      ElMessage.success('登录成功');

      // 重定向到主页
      router.push('/');
    } else {
      errorMessage.value = data.message || '登录失败';
      console.error('登录失败:', data.message);
    }
  } catch (error: any) {
    console.error('登录请求错误:', error);
    if (error.response) {
      errorMessage.value = error.response.data.message || '登录失败，请检查您的用户名和密码';
    } else {
      errorMessage.value = '网络错误，请稍后重试';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
  overflow: hidden;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
  }

  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.login-box {
  position: relative;
  z-index: 2;
  width: 420px;
  padding: 50px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideIn 0.8s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.05);
  }

  100% {
    transform: scale(1);
  }
}

.login-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  color: #7f8c8d;
  font-size: 16px;
  font-weight: 400;
}

.login-form {
  margin-bottom: 30px;
}

.login-form :deep(.el-form-item__label) {
  color: #2c3e50;
  font-weight: 500;
  font-size: 14px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e1e8f0;
  transition: all 0.3s ease;
  padding: 12px 16px;
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: #4f9cf9;
  box-shadow: 0 4px 12px rgba(79, 156, 249, 0.15);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #4f9cf9;
  box-shadow: 0 4px 12px rgba(79, 156, 249, 0.2);
}

.login-button {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #4f9cf9 0%, #1e40af 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(79, 156, 249, 0.3);
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 156, 249, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.login-tips {
  margin-top: 20px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {

  0%,
  100% {
    transform: translateX(0);
  }

  25% {
    transform: translateX(-5px);
  }

  75% {
    transform: translateX(5px);
  }
}

.login-tips :deep(.el-alert) {
  border-radius: 8px;
  border: none;
  background: rgba(245, 108, 108, 0.1);
}

.password-icon {
  cursor: pointer;
  color: #909399;
  transition: color 0.3s ease;
}

.password-icon:hover {
  color: #4f9cf9;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e1e8f0;
}

.login-footer p {
  color: #95a5a6;
  font-size: 12px;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-box {
    width: 90%;
    margin: 20px;
    padding: 30px 20px;
  }

  .login-header h2 {
    font-size: 24px;
  }

  .shape {
    display: none;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .login-box {
    background: rgba(45, 55, 72, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .login-header h2 {
    color: #ffffff;
  }

  .login-header p {
    color: #a0aec0;
  }

  .login-form :deep(.el-form-item__label) {
    color: #e2e8f0;
  }

  .form-input :deep(.el-input__wrapper) {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .login-footer p {
    color: #718096;
  }
}
</style>