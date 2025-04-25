import api from './index';

// 用户登录
export async function login(username: string, password: string) {
  const response =  await api.post('/api/auth/login', { username, password });
  return response.data;
}

// 用户登出
export async function logout() {
  const response =  await api.post('/api/auth/logout');
  return response.data;
}

// 获取当前用户信息
export async function getCurrentUser() {
  const response =  await api.get('/api/auth/current-user');
  return response.data;
}

// 修改密码
export async function changePassword(oldPassword: string, newPassword: string) {
  const response =  await api.post('/api/auth/change-password', {
    old_password: oldPassword,
    new_password: newPassword
  });
  return response.data;
}

// ============= 用户管理 =============

// 获取所有用户 (仅管理员)
export async function getAllUsers() {
  const response =  await api.get('/api/auth/users');
  return response.data;
}

// 创建用户 (仅管理员)
export async function createUser(userData: {
  username: string;
  password: string;
  fullname?: string;
  email?: string;
  is_admin?: boolean;
  tenant_ids?: number[];
}) {
  const response =  await api.post('/api/auth/users', userData);
  return response.data;
}

// 更新用户 (仅管理员)
export async function updateUser(
  userId: number,
  userData: {
    username?: string;
    fullname?: string;
    email?: string;
    password?: string;
    is_admin?: boolean;
    status?: string;
    tenant_ids?: number[];
  }
) {
  const response =  await api.put(`/api/auth/users/${userId}`, userData);
  return response.data;
}

// 删除用户 (仅管理员)
export async function deleteUser(userId: number) {
  const response =  await api.delete(`/api/auth/users/${userId}`);
  return response.data;
}

// ============= 租户管理 =============

// 获取所有租户 (仅管理员)
export async function getAllTenants() {
  const response =  await api.get('/api/auth/tenants');
  return response.data;
}

// 创建租户 (仅管理员)
export async function createTenant(tenantData: {
  name: string;
  code: string;
  description?: string;
}) {
  const response =  await api.post('/api/auth/tenants', tenantData);
  return response.data;
}

// 更新租户 (仅管理员)
export async function updateTenant(
  tenantId: number,
  tenantData: {
    name?: string;
    description?: string;
    status?: string;
  }
) {
  const response =  await api.put(`/api/auth/tenants/${tenantId}`, tenantData);
  return response.data;
}

// 删除租户 (仅管理员)
export async function deleteTenant(tenantId: number) {
  const response =  await api.delete(`/api/auth/tenants/${tenantId}`);
  return response.data;
} 