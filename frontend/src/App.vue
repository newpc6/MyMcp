<template>
  <el-container class="app-container">
    <el-header padding="0" v-if="showNavbar">
      <NavbarComponent />
    </el-header>
    
    <el-main :class="{ 'login-main': !showNavbar }">
      <router-view></router-view>
    </el-main>
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

.login-main {
  padding: 0;
}
</style>
