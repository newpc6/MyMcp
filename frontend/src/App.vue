<template>
  <el-container class="app-container" :class="{ 'is-login': !showNavbar }">
    <el-aside v-if="showNavbar" width="232px" class="app-sidebar">
      <NavbarComponent />
    </el-aside>

    <el-container class="app-workspace">
      <el-header v-if="showNavbar" height="52px" class="app-header">
        <div class="app-header-title">
          <span class="app-header-label">当前位置</span>
          <span>{{ currentTitle }}</span>
        </div>
        <div class="app-header-actions">
          <span class="app-header-meta">MCP 管理平台</span>
          <span class="app-header-user">{{ username }}</span>
        </div>
      </el-header>

      <el-main class="app-main" :class="{ 'login-main': !showNavbar }">
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavbarComponent from './components/NavbarComponent.vue'

const route = useRoute()

// 根据路由判断是否显示导航栏
const showNavbar = computed(() => {
  // 在登录页面不显示导航栏
  return route.name !== 'login'
})

const currentTitle = computed(() => String(route.meta?.title || 'MCP 管理平台'))

const username = computed(() => {
  try {
    const userInfo = localStorage.getItem('userInfo')
    return userInfo ? JSON.parse(userInfo).username || 'admin' : '未登录'
  } catch (error) {
    return '未登录'
  }
})

onMounted(async () => {
  // 页面初始化时可以加载一些全局数据
  console.log('App mounted')
})
</script>

<style>
.app-container {
  height: 100vh;
  display: flex;
  background: var(--common-background-color);
}

.app-container.is-login {
  display: block;
}

.app-sidebar {
  padding: 0;
  overflow: hidden;
  background-image: var(--menu-background-image);
}

.app-workspace {
  min-width: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--common-background-color);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 0 0 52px;
  padding: 0 16px;
  background: var(--header-background-color);
  border-bottom: 1px solid var(--header-border-color);
  box-shadow: 0 1px 0 0 var(--header-border-color);
}

.app-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  color: var(--common-text-color-heavy);
  font-size: 14px;
  font-weight: 600;
  line-height: 24px;
}

.app-header-title::before {
  width: 3px;
  height: 16px;
  margin-right: 8px;
  border-radius: var(--common-radius-sm);
  background: var(--common-primary-color);
  content: '';
}

.app-header-label {
  color: var(--common-text-color-light);
  font-size: 12px;
  font-weight: 400;
}

.app-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--common-text-color-light);
  font-size: 12px;
  line-height: 20px;
}

.app-header-user {
  height: 28px;
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  color: var(--common-text-color);
  background: var(--common-hover-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-md);
}

.app-main {
  height: 0;
  padding: 8px;
  flex: 1;
  overflow-y: auto;
  background: var(--common-background-color);
  min-width: 0;
}

.login-main {
  padding: 0;
  height: 100vh;
}
</style>
