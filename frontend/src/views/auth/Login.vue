<template>
  <div class="login-container">
    <section class="login-shell">
      <div class="login-brand-panel">
        <div class="brand-mark">
          <img src="/app-icon.svg" alt="MCP 管理平台" />
        </div>
        <div>
          <h1>MCP 管理平台</h1>
          <p>统一管理 MCP 模板、服务发布、密钥和调用审计。</p>
        </div>
        <div class="brand-meta">
          <div>
            <span>服务治理</span>
            <strong>运行监控 / 访问控制</strong>
          </div>
          <div>
            <span>模板管理</span>
            <strong>分类维护 / 快速复用</strong>
          </div>
          <div>
            <span>安全审计</span>
            <strong>密钥管理 / 调用日志</strong>
          </div>
        </div>
      </div>

      <div class="login-box">
        <div class="login-header">
          <h2>账号登录</h2>
          <p>请输入账号信息进入管理控制台</p>
        </div>

        <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top" class="login-form"
          size="large">
          <el-form-item prop="username" label="用户名">
            <el-input v-model="loginForm.username" :prefix-icon="User" placeholder="请输入用户名" class="form-input" />
          </el-form-item>

          <el-form-item prop="password" label="密码">
            <el-input v-model="loginForm.password" :prefix-icon="Lock" :type="passwordVisible ? 'text' : 'password'"
              placeholder="请输入密码" class="form-input" @keyup.enter="handleLogin">
              <template #suffix>
                <el-icon class="password-icon" @click="passwordVisible = !passwordVisible">
                  <View v-if="passwordVisible" />
                  <Hide v-else />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" class="login-button" size="large" @click="handleLogin">
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-tips" v-if="errorMessage">
          <el-alert :title="errorMessage" type="error" show-icon :closable="false" />
        </div>

        <div class="login-footer">
          MCP Admin Console
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance } from 'element-plus';
import { login } from '@/api/auth';
import { View, Hide, User, Lock } from '@element-plus/icons-vue';

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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 40px;
  background: var(--common-background-color);
}

.login-shell {
  width: min(980px, 100%);
  min-height: 560px;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) 420px;
  overflow: hidden;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-lg);
  box-shadow: var(--common-shadow-sm);
}

.login-brand-panel {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px;
  color: var(--common-on-primary-color);
  background: var(--common-primary-gradient);
}

.brand-mark {
  width: 48px;
  height: 48px;
  margin-bottom: 24px;
  border-radius: var(--common-radius-md);
  box-shadow: 0 14px 30px rgb(5 46 111 / 28%);
}

.brand-mark img {
  width: 100%;
  height: 100%;
  display: block;
}

.login-brand-panel h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
  line-height: 40px;
}

.login-brand-panel p {
  max-width: 390px;
  margin: 12px 0 0;
  color: var(--common-on-primary-muted-color);
  font-size: var(--common-font-size-base);
  line-height: 24px;
}

.brand-meta {
  display: grid;
  gap: 12px;
}

.brand-meta div {
  padding: 14px 16px;
  background: rgb(255 255 255 / 10%);
  border: 1px solid rgb(255 255 255 / 18%);
  border-radius: var(--common-radius-md);
}

.brand-meta span,
.brand-meta strong {
  display: block;
}

.brand-meta span {
  color: var(--common-on-primary-muted-color);
  font-size: var(--common-font-size-secondary);
}

.brand-meta strong {
  margin-top: 4px;
  font-size: var(--common-font-size-base);
  font-weight: 600;
}

.login-box {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 40px;
  background: var(--common-panel-background-color);
}

.login-header {
  margin-bottom: 28px;
}

.login-header h2 {
  margin: 0;
  color: var(--common-text-color-heavy);
  font-size: 24px;
  font-weight: 700;
  line-height: 32px;
}

.login-header p {
  margin: 6px 0 0;
  color: var(--common-text-color-light);
  font-size: var(--common-font-size-base);
}

.login-form {
  margin-bottom: 16px;
}

.login-form :deep(.el-form-item__label) {
  color: var(--common-text-color);
  font-size: var(--common-font-size-base);
  font-weight: 600;
}

.form-input :deep(.el-input__wrapper) {
  min-height: 42px;
  padding: 0 12px;
  border-radius: var(--common-radius-md);
  box-shadow: 0 0 0 1px var(--common-input-border-color) inset;
  transition: box-shadow 0.2s ease;
}

.form-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--common-primary-color) inset;
}

.form-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--common-primary-color) inset, 0 0 0 3px var(--zartd-primary-fade-10);
}

.login-button {
  width: 100%;
  height: 44px;
  border-radius: var(--common-radius-md);
  font-size: var(--common-font-size-base);
  font-weight: 600;
  background: var(--common-primary-color);
  border: none;
  box-shadow: none;
  transition: background-color 0.2s ease;
}

.login-button:hover {
  background: var(--zartd-primary-7);
}

.login-tips {
  margin-top: 16px;
}

.login-tips :deep(.el-alert) {
  border-radius: var(--common-radius-md);
}

.password-icon {
  cursor: pointer;
  color: var(--common-text-color-lighter);
  transition: color 0.2s ease;
}

.password-icon:hover {
  color: var(--common-primary-color);
}

.login-footer {
  text-align: center;
  margin-top: 16px;
  padding-top: 16px;
  color: var(--common-text-color-lighter);
  font-size: var(--common-font-size-secondary);
  border-top: 1px solid var(--common-border-color);
}

@media (max-width: 860px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-brand-panel {
    display: none;
  }

  .login-container {
    padding: 20px;
  }
}
</style>
