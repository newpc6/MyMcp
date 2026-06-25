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
    redirect: '/mcp-templates'
  },
  {
    path: '/mcp-templates',
    name: 'mcp_templates',
    component: () => import('../views/mcp_template/index.vue'),
    meta: { title: 'MCP 模板广场' }
  },
  {
    path: '/mcp-templates/:id',
    name: 'mcp-template-detail',
    component: () => import('../views/mcp_template/McpTemplateDetail.vue'),
    meta: { title: 'MCP 模板详情' }
  },
  {
    path: '/server',
    name: 'server',
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
  },
  {
    path: '/system',
    name: 'system-management',
    component: () => import('../views/system/index.vue'),
    meta: { title: '系统管理', adminOnly: true }
  },
  {
    path: '/system/python-packages',
    name: 'python-packages',
    component: () => import('../views/system/PythonPackages.vue'),
    meta: { title: 'Python包管理', adminOnly: true }
  },
  {
    path: '/system/scheduled-tasks',
    name: 'scheduled-tasks',
    component: () => import('../views/system/ScheduledTasks.vue'),
    meta: { title: '定时任务管理', adminOnly: true }
  },
  // 鉴权管理路由
  {
    path: '/mcp-auth/secret-management',
    name: 'mcp-auth-secret-management',
    component: () => import('../views/mcp-auth/SecretManagement.vue'),
    meta: { title: '密钥管理' }
  },
  {
    path: '/mcp-auth/access-logs',
    name: 'mcp-auth-access-logs',
    component: () => import('../views/mcp-auth/AccessLogs.vue'),
    meta: { title: '访问日志' }
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
  let isAuthenticated = false;
  let userInfo = null;

  if (userInfoStr) {
    try {
      userInfo = JSON.parse(userInfoStr);
      // 简单验证用户信息结构
      isAuthenticated = !!(userInfo && userInfo.user_id && userInfo.token);
    } catch (e) {
      console.warn('用户信息格式错误，清除localStorage');
      localStorage.removeItem('userInfo');
      isAuthenticated = false;
    }
  }

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
    console.warn('用户未认证，重定向到登录页');
    next({ name: 'login' });
    return;
  }

  // 检查管理员权限
  if (toMeta.adminOnly) {
    try {
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
