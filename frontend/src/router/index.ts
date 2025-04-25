import { createRouter, createWebHistory, RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import Home from '../views/Home.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    name: 'home',
    // component: Home,
    meta: { title: '首页' },
    redirect: '/marketplace'
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
    component: () => import('../views/mcp/index.vue'),
    meta: { title: 'MCP 服务管理' }
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('../views/auth/Users.vue'),
    meta: { title: '用户管理', adminOnly: true }
  },
  {
    path: '/tenants',
    name: 'tenants',
    component: () => import('../views/auth/Tenants.vue'),
    meta: { title: '租户管理', adminOnly: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/statictics/index.vue'),
    meta: { requiresAdmin: true, title: 'MCP统计' }
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
  const toMeta = to.meta as { title?: string; public?: boolean; adminOnly?: boolean };
  document.title = toMeta.title ? `${toMeta.title} - MCP管理平台` : 'MCP管理平台';
  
  // 检查用户认证状态
  const userInfoStr = localStorage.getItem('userInfo');
  const isAuthenticated = !!userInfoStr;
  
  // 如果是公开页面，直接通过
  if (toMeta.public) {
    // 如果已经登录，并且请求的是登录页，重定向到首页
    if (isAuthenticated && to.name === 'login') {
      next({ name: 'home' });
    } else {
      next();
    }
    return;
  }
  
  // 如果未登录，重定向到登录页
  if (!isAuthenticated) {
    next({ name: 'login' });
    return;
  }
  
  // 检查管理员权限
  if (toMeta.adminOnly) {
    try {
      const userInfo = JSON.parse(userInfoStr);
      if (!userInfo.is_admin) {
        next({ name: 'home' });
        return;
      }
    } catch (e) {
      next({ name: 'login' });
      return;
    }
  }
  
  next();
});

export default router 