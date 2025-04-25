<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>智能MCP管理平台</h2>
        <p>请登录您的账号</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        label-position="top"
        class="login-form"
      >
        <el-form-item prop="username" label="用户名">
          <el-input 
            v-model="loginForm.username" 
            prefix-icon="User" 
            placeholder="请输入用户名"
          />
        </el-form-item>
        
        <el-form-item prop="password" label="密码">
          <el-input 
            v-model="loginForm.password" 
            prefix-icon="Lock" 
            :type="passwordVisible ? 'text' : 'password'" 
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          >
            <template #suffix>
              <el-icon 
                class="password-icon" 
                @click="passwordVisible = !passwordVisible"
              >
                <component :is="passwordVisible ? 'View' : 'Hide'" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-button" 
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-tips" v-if="errorMessage">
        <el-alert :title="errorMessage" type="error" show-icon :closable="false" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance } from 'element-plus';
import { login } from '@/api/auth';
import { View, Hide } from '@element-plus/icons-vue';

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
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f7fa;
}

.login-box {
  width: 400px;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  background: white;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.login-tips {
  margin-top: 20px;
}

.password-icon {
  cursor: pointer;
  color: #909399;
}

.password-icon:hover {
  color: #409EFF;
}
</style> 