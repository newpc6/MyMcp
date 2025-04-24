import { createRouter, createWebHistory, RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import Home from '../views/Home.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { title: '首页' }
  },
  // {
  //   path: '/tools',
  //   name: 'tools',
  //   component: () => import('../views/tools/ToolsList.vue'),
  //   meta: { title: 'MCP 工具管理' }
  // },
  {
    path: '/modules',
    name: 'modules',
    component: () => import('../views/modules/index.vue'),
    meta: { title: 'MCP 模块管理' }
  },
  {
    path: '/marketplace',
    name: 'marketplace',
    component: () => import('../views/marketplace/index.vue'),
    meta: { title: 'MCP 市场管理' }
  },
  {
    path: '/marketplace/:id',
    name: 'module-detail',
    component: () => import('../views/marketplace/ModuleDetail.vue'),
    meta: { title: 'MCP 模块详情' }
  },
  {
    path: '/mcp-services',
    name: 'mcp-services',
    component: () => import('../views/mcp/ServicesList.vue'),
    meta: { title: 'MCP 服务管理' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 设置页面标题
router.beforeEach((
  to: RouteLocationNormalized, 
  from: RouteLocationNormalized, 
  next: NavigationGuardNext
) => {
  const toMeta = to.meta as { title?: string };
  document.title = toMeta.title ? `${toMeta.title} - 智能MCP管理平台` : '智能MCP管理平台';
  next();
});

export default router 