import axios from 'axios';
import type { ToolInfo, ToolContent, ToolCreate, ToolUpdate } from '../types/tools';

const API_BASE_URL = '/api';

/**
 * 获取所有工具信息
 */
export async function getTools() {
  const response = await axios.get<ToolInfo[]>(`${API_BASE_URL}/tools`);
  return response.data;
}

/**
 * 获取工具列表 (带详细信息)
 */
export async function listTools() {
  const response = await axios.get<ToolInfo[]>(`${API_BASE_URL}/tools/list`);
  return response.data;
}

/**
 * 获取工具内容
 * @param toolPath 工具路径
 */
export async function getToolContent(toolPath: string) {
  const response = await axios.get<ToolContent>(`${API_BASE_URL}/tools/${encodeURIComponent(toolPath)}`);
  return response.data;
}

/**
 * 获取特定工具信息
 * @param toolName 工具名称
 */
export async function getToolInfo(toolName: string) {
  const response = await axios.get(`${API_BASE_URL}/tools/info/${encodeURIComponent(toolName)}`);
  return response.data;
}

/**
 * 创建新工具
 * @param toolData 工具创建数据
 */
export async function createTool(toolData: ToolCreate) {
  const response = await axios.post(`${API_BASE_URL}/tools`, toolData);
  return response.data;
}

/**
 * 更新工具内容
 * @param toolPath 工具路径
 * @param toolData 工具更新数据
 */
export async function updateTool(toolPath: string, toolData: ToolUpdate) {
  const response = await axios.put(`${API_BASE_URL}/tools/${encodeURIComponent(toolPath)}`, toolData);
  return response.data;
}

/**
 * 删除工具
 * @param toolPath 工具路径
 */
export async function deleteTool(toolPath: string) {
  const response = await axios.delete(`${API_BASE_URL}/tools/${encodeURIComponent(toolPath)}`);
  return response.data;
} 