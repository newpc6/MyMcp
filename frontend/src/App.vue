<template>
  <el-container class="app-container">
    <el-header padding="0">
      <NavbarComponent />
    </el-header>
    
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import NavbarComponent from './components/NavbarComponent.vue'

onMounted(async () => {
  // 页面初始化时可以加载一些全局数据
  console.log('App mounted')
})
</script>

<style>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  padding: 0;
  height: auto;
  z-index: 10;
}

.el-main {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}
</style>
