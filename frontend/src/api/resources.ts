import api from './index';
import type { ResourceInfo, ResourceContent, ResourceCreate, ResourceUpdate } from '../types/resources';

const API_BASE_URL = '/api';

/** 获取所有资源信息 */
export const getResources = async (): Promise<ResourceInfo[]> => {
  const response = await api.get(`${API_BASE_URL}/resources`);
  // 如果后端返回的是对象格式，需要转换为数组
  const resourcesData = response.data.data;
  return typeof resourcesData === 'object' && !Array.isArray(resourcesData) 
    ? Object.values(resourcesData) 
    : resourcesData;
};

/** 获取所有资源路径列表 */
export const listResources = async (): Promise<string[]> => {
  const response = await api.get(`${API_BASE_URL}/resources/list`);
  return response.data.data;
};

/** 获取特定资源信息 */
export const getResourceInfo = async (resourcePath: string): Promise<ResourceInfo> => {
  const response = await api.get(`${API_BASE_URL}/resources/info/${encodeURIComponent(resourcePath)}`);
  return response.data.data;
};

/** 获取资源内容 */
export const getResourceContent = async (resourcePath: string): Promise<ResourceContent> => {
  const response = await api.get(`${API_BASE_URL}/resources/${encodeURIComponent(resourcePath)}`);
  return response.data.data;
};

/** 创建新资源 */
export const createResource = async (resourceData: ResourceCreate): Promise<{ message: string }> => {
  const response = await api.post(`${API_BASE_URL}/resources`, resourceData);
  return response.data.data;
};

/** 更新资源内容 */
export const updateResource = async (resourcePath: string, resourceData: ResourceUpdate): Promise<{ message: string }> => {
  const response = await api.put(`${API_BASE_URL}/resources/${encodeURIComponent(resourcePath)}`, resourceData);
  return response.data.data;
};

/** 删除资源 */
export const deleteResource = async (resourcePath: string): Promise<{ message: string }> => {
  const response = await api.delete(`${API_BASE_URL}/resources/${encodeURIComponent(resourcePath)}`);
  return response.data.data;
}; 