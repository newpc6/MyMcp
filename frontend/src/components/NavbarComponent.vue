<template>
  <div class="navbar-container">
    <el-menu
      mode="horizontal"
      router
      :ellipsis="false"
      class="nav-menu"
    >
      <div class="flex-grow logo-container">
        <h1 class="text-xl font-bold text-primary">智能MCP管理平台</h1>
      </div>
      
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/tools">工具管理</el-menu-item>
      <el-menu-item index="/mcp">服务状态</el-menu-item>
      <el-menu-item index="/resources">资源管理</el-menu-item>
      <el-menu-item index="/protocols">协议管理</el-menu-item>
      
      <div class="version-info">
        <span class="text-sm">版本: v1.0.0</span>
      </div>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'NavbarComponent'
});
</script>

<style scoped>
.navbar-container {
  border-bottom: solid 1px var(--el-menu-border-color);
}

.nav-menu {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 20px;
}

.flex-grow {
  flex-grow: 1;
}

.logo-container {
  display: flex;
  align-items: center;
  padding-right: 20px;
}

.text-primary {
  color: var(--el-color-primary);
}

.version-info {
  display: flex;
  align-items: center;
  padding: 0 20px;
  color: var(--el-text-color-secondary);
}

:deep(.el-menu-item) {
  font-size: 14px;
}

:deep(.el-menu--horizontal) {
  border-bottom: none;
}
</style> 