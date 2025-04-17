<template>
  <el-container class="app-container">
    <el-header>
      <el-menu
        mode="horizontal"
        :router="true"
        class="main-menu"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/tools">工具管理</el-menu-item>
        <!-- <el-menu-item index="/modules">模块管理</el-menu-item> -->
      </el-menu>
    </el-header>
    
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useMCPStore } from '@/store'

const store = useMCPStore()

onMounted(async () => {
  await store.fetchTools()
  await store.fetchResources()
  await store.fetchModules()
})
</script>

<style>
.app-container {
  height: 100vh;
}

.main-menu {
  border-bottom: none;
}

.el-header {
  padding: 0;
  height: 60px;
}

.el-main {
  padding: 20px;
}
</style>
