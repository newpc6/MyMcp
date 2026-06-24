<template>
  <div class="app-container" :class="{ 'is-login': !showNavbar }">
    <template v-if="showNavbar">
      <header class="app-header">
        <div class="app-brand" @click="goHome">
          <div class="app-brand-mark">MCP</div>
          <div class="app-brand-text">
            <div class="app-brand-title">MCP 管理平台</div>
            <div class="app-brand-subtitle">Admin Console</div>
          </div>
        </div>

        <div class="app-header-right">
          <div class="app-user-meta">
            <div class="app-user-name">{{ username }}</div>
            <div class="app-user-role">{{ userRole }}</div>
          </div>
          <el-avatar class="app-avatar">{{ userInitial }}</el-avatar>
          <el-dropdown @command="handleHeaderCommand">
            <span class="app-dropdown-link">
              <el-icon><Operation /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <div class="app-body">
        <el-aside width="220px" class="app-sidebar">
          <NavbarComponent />
        </el-aside>

        <section class="app-workspace">
          <div class="app-tabs">
            <el-tabs
              v-model="activeTab"
              type="card"
              closable
              class="app-tabs-bar"
              :class="{ 'hide-close-btn': openedTabs.length === 1 }"
              @tab-click="handleTabClick"
              @tab-remove="handleTabRemove"
            >
              <el-tab-pane
                v-for="tab in openedTabs"
                :key="tab.path"
                :label="tab.title"
                :name="tab.path"
                :closable="tab.path !== '/marketplace'"
              />
            </el-tabs>
          </div>

          <main class="app-main">
            <router-view></router-view>
          </main>
        </section>
      </div>
    </template>

    <main v-else class="login-main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { TabsPaneContext, TabPaneName } from 'element-plus'
import { ElMessage } from 'element-plus'
import { Operation } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import NavbarComponent from './components/NavbarComponent.vue'
import { logout } from '@/api/auth'

const route = useRoute()
const router = useRouter()

interface OpenedTab {
  path: string
  title: string
}

const openedTabs = ref<OpenedTab[]>([])
const activeTab = ref('')

// 根据路由判断是否显示导航栏
const showNavbar = computed(() => {
  // 在登录页面不显示导航栏
  return route.name !== 'login'
})

const currentTitle = computed(() => String(route.meta?.title || 'MCP 管理平台'))

const currentUser = computed(() => {
  try {
    const userInfo = localStorage.getItem('userInfo')
    return userInfo ? JSON.parse(userInfo) : null
  } catch (error) {
    return null
  }
})

const username = computed(() => currentUser.value?.username || 'admin')
const userRole = computed(() => currentUser.value?.is_admin ? '系统管理员' : '系统用户')
const userInitial = computed(() => username.value.slice(0, 1).toUpperCase())

const syncOpenedTabs = () => {
  if (!showNavbar.value) return

  const path = route.path
  const title = currentTitle.value
  activeTab.value = path

  if (!openedTabs.value.some((tab) => tab.path === path)) {
    openedTabs.value.push({ path, title })
  }
}

const handleTabClick = (pane: TabsPaneContext) => {
  const nextPath = String(pane.paneName || '')
  if (nextPath && nextPath !== route.path) {
    router.push(nextPath)
  }
}

const handleTabRemove = (name: TabPaneName) => {
  const path = String(name)
  const index = openedTabs.value.findIndex((tab) => tab.path === path)
  if (index < 0 || openedTabs.value.length === 1) return

  openedTabs.value.splice(index, 1)

  if (path === route.path) {
    const nextTab = openedTabs.value[index] || openedTabs.value[index - 1]
    router.push(nextTab?.path || '/marketplace')
  }
}

const handleHeaderCommand = async (command: string) => {
  if (command !== 'logout') return

  try {
    await logout()
    ElMessage.success('退出登录成功')
  } catch (error) {
    console.error('登出API调用失败', error)
  } finally {
    localStorage.removeItem('userInfo')
    router.push('/login')
  }
}

const goHome = () => {
  router.push('/')
}

watch(() => route.fullPath, syncOpenedTabs, { immediate: true })

onMounted(async () => {
  // 页面初始化时可以加载一些全局数据
  console.log('App mounted')
})
</script>

<style>
.app-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--common-background-color);
  overflow: hidden;
}

.app-container.is-login {
  display: block;
}

.app-header {
  height: 60px;
  flex: 0 0 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--header-background-color);
  box-shadow: var(--common-shadow-sm);
}

.app-brand,
.app-header-right {
  display: flex;
  align-items: center;
  min-width: 0;
}

.app-brand {
  gap: 8px;
  cursor: pointer;
}

.app-brand-mark {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--common-on-primary-color);
  background: var(--common-on-primary-surface-color);
  border-radius: var(--common-radius-md);
  box-shadow: var(--common-shadow-xs);
  font-size: 14px;
  font-weight: 700;
}

.app-brand-text {
  min-width: 0;
  color: var(--common-on-primary-color);
  line-height: 1.2;
}

.app-brand-title {
  font-size: var(--common-font-size-title-md);
  font-weight: 700;
}

.app-brand-subtitle {
  margin-top: 3px;
  color: var(--common-on-primary-muted-color);
  font-size: var(--common-font-size-secondary);
}

.app-header-right {
  gap: 12px;
  color: var(--common-on-primary-color);
}

.app-user-meta {
  text-align: right;
  line-height: 1.2;
}

.app-user-name {
  font-size: var(--common-font-size-base);
  font-weight: 600;
}

.app-user-role {
  margin-top: 3px;
  color: var(--common-on-primary-muted-color);
  font-size: var(--common-font-size-secondary);
}

.app-avatar {
  background: var(--zartd-primary-6) !important;
  border: 2px solid var(--common-on-primary-border-strong-color);
}

.app-dropdown-link {
  display: inline-flex;
  align-items: center;
  color: var(--common-on-primary-color);
  cursor: pointer;
}

.app-body {
  height: calc(100vh - 60px);
  display: flex;
  min-height: 0;
}

.app-sidebar {
  flex: 0 0 220px;
  padding: 0;
  overflow: hidden;
  background: var(--menu-background-color) !important;
  border-right: 1px solid var(--common-border-color);
  box-shadow: var(--common-shadow-xs);
}

.app-workspace {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--common-background-color);
}

.app-tabs {
  height: 50px;
  flex: 0 0 50px;
  display: flex;
  align-items: flex-end;
  padding: 0 16px;
  background: var(--common-surface-gradient);
  box-shadow: var(--common-shadow-xs);
}

.app-tabs-bar {
  width: 100%;
}

.app-tabs-bar .el-tabs__header {
  height: 50px;
  display: flex;
  align-items: flex-end;
  margin: 0;
}

.app-tabs-bar .el-tabs__nav-wrap {
  height: 50px;
  display: flex;
  align-items: flex-end;
}

.app-tabs-bar .el-tabs__nav-wrap::after {
  display: none;
}

.app-tabs-bar .el-tabs__nav-scroll {
  display: flex;
  align-items: flex-end;
}

.app-tabs-bar .el-tabs__nav {
  border: 0 !important;
}

.app-tabs-bar .el-tabs__item {
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 34px;
  margin-right: 2px;
  padding: 0 12px !important;
  color: var(--common-text-color-light);
  background: var(--zartd-g-20);
  border: 1px solid var(--common-border-color);
  border-bottom: 0;
  border-radius: var(--common-radius-md) var(--common-radius-md) 0 0;
  font-size: var(--common-font-size-base);
}

.app-tabs-bar .el-tabs__item.is-active {
  position: relative;
  z-index: 1;
  color: var(--common-primary-color);
  background: var(--common-surface-gradient);
  box-shadow: var(--common-shadow-xs);
  font-weight: 500;
}

.app-tabs-bar .el-icon.is-icon-close {
  width: 14px;
  height: 14px;
  margin-left: 6px;
  border-radius: var(--common-radius-sm);
}

.app-tabs-bar .el-icon.is-icon-close:hover {
  color: var(--common-primary-color);
  background: var(--common-primary-background-color);
}

.app-tabs-bar .el-tabs__content {
  display: none;
}

.app-tabs-bar.hide-close-btn .el-icon.is-icon-close {
  display: none;
}

.app-main {
  min-height: 0;
  padding: 20px;
  flex: 1;
  overflow: auto;
  background-color: var(--common-background-color);
  background-image: var(--common-workspace-grid), var(--common-workspace-background);
  background-size: 24px 24px, auto;
  background-position: -1px -1px, 0 0;
}

.login-main {
  padding: 0;
  height: 100vh;
}
</style>
