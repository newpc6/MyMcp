import { createRouter, createWebHistory, RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/tools',
    name: 'tools',
    component: () => import('../views/tools/index.vue'),
    meta: { title: 'MCP 工具管理' }
  },
  {
    path: '/mcp',
    name: 'mcp',
    component: () => import('../views/mcp/index.vue'),
    meta: { title: 'MCP 服务状态' }
  },
  {
    path: '/resources',
    name: 'resources',
    component: () => import('../views/resources/index.vue'),
    meta: { title: 'MCP 资源管理' }
  },
  // {
  //   path: '/modules',
  //   name: 'modules',
  //   component: () => import('../views/modules/index.vue'),
  //   meta: { title: 'MCP 模块管理' }
  // },
  {
    path: '/protocols',
    name: 'protocols',
    component: () => import('../views/protocols/index.vue'),
    meta: { title: 'MCP 协议管理' }
  },
  {
    path: '/editor/:path*',
    name: 'Editor',
    component: () => import('../views/Editor.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
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