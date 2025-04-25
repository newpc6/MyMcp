import api from './index';
import type { ToolInfo, ToolContent, ToolCreate, ToolUpdate } from '../types/tools';

const API_BASE_URL = '/api';

/**
 * 获取所有工具信息
 */
export async function getTools() {
  const response = await api.get(`${API_BASE_URL}/tools`);
  return response.data.data;
}

/**
 * 获取工具列表 (带详细信息)
 */
export async function listTools() {
  const response = await api.get(`${API_BASE_URL}/tools/list`);
  return response.data.data;
}

/**
 * 获取工具内容
 * @param toolPath 工具路径
 */
export async function getToolContent(toolPath: string) {
  const response = await api.get(`${API_BASE_URL}/tools/${encodeURIComponent(toolPath)}`);
  return response.data.data;
}

/**
 * 获取特定工具信息
 * @param toolName 工具名称
 */
export async function getToolInfo(toolName: string) {
  const response = await api.get(`${API_BASE_URL}/tools/info/${encodeURIComponent(toolName)}`);
  return response.data.data;
}

/**
 * 创建新工具
 * @param toolData 工具创建数据
 */
export async function createTool(toolData: ToolCreate) {
  const response = await api.post(`${API_BASE_URL}/tools`, toolData);
  return response.data.data;
}

/**
 * 更新工具内容
 * @param toolPath 工具路径
 * @param toolData 工具更新数据
 */
export async function updateTool(toolPath: string, toolData: ToolUpdate) {
  const response = await api.put(`${API_BASE_URL}/tools/${encodeURIComponent(toolPath)}`, toolData);
  return response.data.data;
}

/**
 * 删除工具
 * @param toolPath 工具路径
 */
export async function deleteTool(toolPath: string) {
  const response = await api.delete(`${API_BASE_URL}/tools/${encodeURIComponent(toolPath)}`);
  return response.data.data;
} 