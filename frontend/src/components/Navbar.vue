<template>
  <nav class="bg-gray-900 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <h1 class="text-xl font-bold text-blue-400">智能MCP管理平台</h1>
          </div>
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <router-link 
                to="/" 
                active-class="bg-gray-800 text-white" 
                exact-active-class="bg-gray-800 text-white"
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
              >
                首页
              </router-link>
              
              <router-link 
                to="/tools" 
                active-class="bg-gray-800 text-white" 
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
              >
                工具管理
              </router-link>
              
              <router-link 
                to="/resources" 
                active-class="bg-gray-800 text-white" 
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
              >
                资源管理
              </router-link>
              
              <router-link 
                to="/modules" 
                active-class="bg-gray-800 text-white" 
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
              >
                模块管理
              </router-link>
              
              <router-link 
                to="/protocols" 
                active-class="bg-gray-800 text-white" 
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
              >
                协议管理
              </router-link>
            </div>
          </div>
        </div>
        <div class="hidden md:block">
          <div class="ml-4 flex items-center md:ml-6">
            <span class="text-sm text-gray-300">版本: v1.0.0</span>
          </div>
        </div>
        <div class="-mr-2 flex md:hidden">
          <!-- 移动端菜单按钮 -->
          <button 
            @click="toggleMobileMenu"
            class="bg-gray-800 inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
          >
            <span class="sr-only">打开主菜单</span>
            <svg 
              :class="{'hidden': mobileMenuOpen, 'block': !mobileMenuOpen}" 
              class="h-6 w-6" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg 
              :class="{'block': mobileMenuOpen, 'hidden': !mobileMenuOpen}" 
              class="h-6 w-6" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 移动端菜单 -->
    <div :class="{'block': mobileMenuOpen, 'hidden': !mobileMenuOpen}" class="md:hidden">
      <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
        <router-link 
          to="/" 
          active-class="bg-gray-800 text-white" 
          exact-active-class="bg-gray-800 text-white"
          class="block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
          @click="mobileMenuOpen = false"
        >
          首页
        </router-link>
        
        <router-link 
          to="/tools" 
          active-class="bg-gray-800 text-white" 
          class="block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
          @click="mobileMenuOpen = false"
        >
          工具管理
        </router-link>
        
        <router-link 
          to="/resources" 
          active-class="bg-gray-800 text-white" 
          class="block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
          @click="mobileMenuOpen = false"
        >
          资源管理
        </router-link>
        
        <router-link 
          to="/modules" 
          active-class="bg-gray-800 text-white" 
          class="block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
          @click="mobileMenuOpen = false"
        >
          模块管理
        </router-link>
        
        <router-link 
          to="/protocols" 
          active-class="bg-gray-800 text-white" 
          class="block px-3 py-2 rounded-md text-base font-medium hover:bg-gray-700"
          @click="mobileMenuOpen = false"
        >
          协议管理
        </router-link>
      </div>
      <div class="pt-4 pb-3 border-t border-gray-700">
        <div class="flex items-center px-5">
          <div class="text-sm text-gray-300">版本: v1.0.0</div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const mobileMenuOpen = ref(false);

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value;
}
</script> 