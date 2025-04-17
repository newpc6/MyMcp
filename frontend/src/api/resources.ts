import api from './index';
import type { ResourceInfo, ResourceContent, ResourceCreate, ResourceUpdate } from '../types/resources';

/** 获取所有资源信息 */
export const getResources = async (): Promise<ResourceInfo[]> => {
  // 注意：后端 /api/resources 返回的是 Dict[str, MCPResourceInfo]
  const response = await api.get<Record<string, ResourceInfo>>('/resources');
  return Object.values(response.data); // 转换为数组
};

/** 获取所有资源路径列表 */
export const listResources = async (): Promise<string[]> => {
  const response = await api.get<string[]>('/resources/list');
  return response.data;
};

/** 获取特定资源信息 */
export const getResourceInfo = async (resourcePath: string): Promise<ResourceInfo> => {
  const response = await api.get<ResourceInfo>(`/resources/info/${encodeURIComponent(resourcePath)}`);
  return response.data;
};

/** 获取资源内容 */
export const getResourceContent = async (resourcePath: string): Promise<ResourceContent> => {
  const response = await api.get<ResourceContent>(`/resources/${encodeURIComponent(resourcePath)}`);
  return response.data;
};

/** 创建新资源 */
export const createResource = async (resourceData: ResourceCreate): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>('/resources', resourceData);
  return response.data;
};

/** 更新资源内容 */
export const updateResource = async (resourcePath: string, resourceData: ResourceUpdate): Promise<{ message: string }> => {
  const response = await api.put<{ message: string }>(`/resources/${encodeURIComponent(resourcePath)}`, resourceData);
  return response.data;
};

/** 删除资源 */
export const deleteResource = async (resourcePath: string): Promise<{ message: string }> => {
  const response = await api.delete<{ message: string }>(`/resources/${encodeURIComponent(resourcePath)}`);
  return response.data;
}; 