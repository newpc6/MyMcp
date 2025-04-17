import api from './index';
import type { ModuleInfo, ModuleContent, ModuleCreate, ModuleUpdate } from '../types/modules';

/** 获取所有模块信息 */
export const getModules = async (): Promise<ModuleInfo[]> => {
  // 注意：后端 /api/modules 返回的是 List[ModuleInfo]
  const response = await api.get<ModuleInfo[]>('/modules');
  return response.data;
};

/** 获取所有模块路径列表 */
export const listModules = async (): Promise<string[]> => {
  const response = await api.get<string[]>('/modules/list');
  return response.data;
};

/** 获取模块内容 */
export const getModuleContent = async (modulePath: string): Promise<ModuleContent> => {
  const response = await api.get<ModuleContent>(`/modules/${encodeURIComponent(modulePath)}`);
  return response.data;
};

/** 创建新模块 */
export const createModule = async (moduleData: ModuleCreate): Promise<{ message: string }> => {
  // 注意：旧代码使用了 FormData，但后端 /api/modules 现在期望 JSON
  // 如果后端修改为接收 FormData，则需要调整回 FormData
  const response = await api.post<{ message: string }>('/modules', moduleData);
  return response.data;
};

/** 更新模块内容 */
export const updateModule = async (modulePath: string, moduleData: ModuleUpdate): Promise<{ message: string }> => {
  const response = await api.put<{ message: string }>(`/modules/${encodeURIComponent(modulePath)}`, moduleData);
  return response.data;
};

/** 删除模块 */
export const deleteModule = async (modulePath: string): Promise<{ message: string }> => {
  const response = await api.delete<{ message: string }>(`/modules/${encodeURIComponent(modulePath)}`);
  return response.data;
}; 