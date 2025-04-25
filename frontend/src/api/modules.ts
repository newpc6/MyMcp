import api from './index';
import type { ModuleInfo, ModuleContent, ModuleCreate, ModuleUpdate } from '../types/modules';

const API_BASE_URL = '/api';

/** 获取所有模块信息 */
export const getModules = async (): Promise<ModuleInfo[]> => {
  const response = await api.get(`${API_BASE_URL}/modules`);
  return response.data.data;
};

/** 获取所有模块路径列表 */
export const listModules = async (): Promise<string[]> => {
  const response = await api.get(`${API_BASE_URL}/modules/list`);
  return response.data.data;
};

/** 获取模块内容 */
export const getModuleContent = async (modulePath: string): Promise<ModuleContent> => {
  const response = await api.get(`${API_BASE_URL}/modules/${encodeURIComponent(modulePath)}`);
  return response.data.data;
};

/** 创建新模块 */
export const createModule = async (moduleData: ModuleCreate): Promise<{ message: string }> => {
  // 注意：旧代码使用了 FormData，但后端 /api/modules 现在期望 JSON
  // 如果后端修改为接收 FormData，则需要调整回 FormData
  const response = await api.post(`${API_BASE_URL}/modules`, moduleData);
  return response.data.data;
};

/** 更新模块内容 */
export const updateModule = async (modulePath: string, moduleData: ModuleUpdate): Promise<{ message: string }> => {
  const response = await api.put(`${API_BASE_URL}/modules/${encodeURIComponent(modulePath)}`, moduleData);
  return response.data.data;
};

/** 删除模块 */
export const deleteModule = async (modulePath: string): Promise<{ message: string }> => {
  const response = await api.delete(`${API_BASE_URL}/modules/${encodeURIComponent(modulePath)}`);
  return response.data.data;
}; 