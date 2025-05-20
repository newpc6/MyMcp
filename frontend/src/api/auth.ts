import api from './index';
import { apiPrefix } from './index';

// 用户登录
export async function login(username: string, password: string) {
  const response =  await api.post(`${apiPrefix}/auth/login`, { username, password });
  return response.data;
}

// 用户登出
export async function logout() {
  const response =  await api.post(`${apiPrefix}/auth/logout`);
  return response.data;
}

// 获取当前用户信息
export async function getCurrentUser() {
  const response =  await api.get(`${apiPrefix}/auth/current-user`);
  return response.data;
}

// 修改密码
export async function changePassword(oldPassword: string, newPassword: string) {
  const response =  await api.post(`${apiPrefix}/auth/change-password`, {
    old_password: oldPassword,
    new_password: newPassword
  });
  return response.data;
}

// ============= 用户管理 =============

// 获取所有用户 (仅管理员)
export async function getAllUsers() {
  const response =  await api.get(`${apiPrefix}/auth/users`);
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
  const response =  await api.post(`${apiPrefix}/auth/users`, userData);
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
  const response =  await api.put(`${apiPrefix}/auth/users/${userId}`, userData);
  return response.data;
}

// 删除用户 (仅管理员)
export async function deleteUser(userId: number) {
  const response =  await api.delete(`${apiPrefix}/auth/users/${userId}`);
  return response.data;
}

// 导入平台用户 (仅管理员)
export async function importPlatformUser(importData: {
  platform_type: string;
  authorization: string;
  tenant_ids?: number[];
}) {
  const response = await api.post(`${apiPrefix}/auth/import-platform-user`, importData);
  return response.data;
}

// ============= 租户管理 =============

// 获取所有租户 (仅管理员)
export async function getAllTenants() {
  const response =  await api.get(`${apiPrefix}/auth/tenants`);
  return response.data;
}

// 获取租户树结构 (仅管理员)
export async function getTenantTree() {
  const response =  await api.get(`${apiPrefix}/auth/tenant-tree`);
  return response.data;
}

// 创建租户 (仅管理员)
export async function createTenant(tenantData: {
  name: string;
  code: string;
  description?: string;
  parent_id?: number;
}) {
  const response =  await api.post(`${apiPrefix}/auth/tenants`, tenantData);
  return response.data;
}

// 更新租户 (仅管理员)
export async function updateTenant(
  tenantId: number,
  tenantData: {
    name?: string;
    description?: string;
    status?: string;
    parent_id?: number;
  }
) {
  const response =  await api.put(`${apiPrefix}/auth/tenants/${tenantId}`, tenantData);
  return response.data;
}

// 删除租户 (仅管理员)
export async function deleteTenant(tenantId: number) {
  const response =  await api.delete(`${apiPrefix}/auth/tenants/${tenantId}`);
  return response.data;
} 