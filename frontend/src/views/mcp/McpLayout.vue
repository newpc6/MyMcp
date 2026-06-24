<template>
  <div class="mcp-layout">
    <!-- 左侧菜单 -->
    <div class="mcp-sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">
          <el-icon class="title-icon">
            <Promotion />
          </el-icon>
          MCP管理
        </h2>
      </div>
      
      <div class="sidebar-menu">
        <el-menu
          :default-active="activeMenu"
          class="mcp-menu"
          @select="handleMenuSelect">
          
          <el-menu-item index="services">
            <el-icon>
              <Grid />
            </el-icon>
            <span>MCP服务管理</span>
          </el-menu-item>
          
          <el-menu-item index="secret-management">
            <el-icon>
              <Key />
            </el-icon>
            <span>密钥管理</span>
          </el-menu-item>
          
          <el-menu-item index="access-logs">
            <el-icon>
              <Document />
            </el-icon>
            <span>访问日志</span>
          </el-menu-item>
        </el-menu>
      </div>
    </div>

    <!-- 右侧内容区域 -->
    <div class="mcp-content">
      <component :is="currentComponent" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Grid, Key, Document, Promotion } from '@element-plus/icons-vue'

// 动态导入页面组件
const McpServices = defineAsyncComponent(() => import('./index.vue'))
const SecretManagement = defineAsyncComponent(() => import('../mcp-auth/SecretManagement.vue'))
const AccessLogs = defineAsyncComponent(() => import('../mcp-auth/AccessLogs.vue'))

const route = useRoute()
const router = useRouter()

// 当前激活的菜单项
const activeMenu = ref('services')

// 组件映射
const componentMap = {
  services: McpServices,
  'secret-management': SecretManagement,
  'access-logs': AccessLogs
}

// 当前显示的组件
const currentComponent = computed(() => {
  return componentMap[activeMenu.value as keyof typeof componentMap]
})

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  
  // 更新路由参数
  const query = { ...route.query, tab: index }
  router.push({ query })
}

// 初始化时根据路由参数设置当前菜单
onMounted(() => {
  const tab = route.query.tab as string
  if (tab && componentMap[tab as keyof typeof componentMap]) {
    activeMenu.value = tab
  }
})
</script>

<style scoped>
.mcp-layout {
  display: flex;
  min-height: calc(100vh - 32px);
  background: var(--common-background-color);
  gap: 12px;
}

.mcp-sidebar {
  width: 216px;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-lg);
  display: flex;
  flex-direction: column;
  box-shadow: var(--common-shadow-sm);
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--common-border-color);
  background: var(--common-panel-background-color);
}

.sidebar-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--common-text-color-heavy);
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 18px;
  color: var(--common-primary-color);
}

.sidebar-menu {
  flex: 1;
  padding: 16px 0;
}

.mcp-menu {
  border: none;
  background: transparent;
}

.mcp-menu .el-menu-item {
  height: 40px;
  line-height: 40px;
  margin: 4px 10px;
  border-radius: var(--common-radius-md);
  font-size: 14px;
  font-weight: 500;
  color: var(--common-text-color);
  transition: background-color 0.2s ease, color 0.2s ease;
}

.mcp-menu .el-menu-item:hover {
  background: var(--common-primary-background-color);
  color: var(--common-primary-color);
}

.mcp-menu .el-menu-item.is-active {
  background: var(--common-primary-color);
  color: var(--common-text-color-positive);
}

.mcp-menu .el-menu-item .el-icon {
  margin-right: 12px;
  font-size: 16px;
}

.mcp-content {
  flex: 1;
  overflow: auto;
  min-width: 0;
  padding: 0;
  background: transparent;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mcp-layout {
    flex-direction: column;
  }
  
  .mcp-sidebar {
    width: 100%;
    height: auto;
  }
  
  .mcp-content {
    margin: 10px;
    padding: 15px;
  }
}
</style>
