/**
 * MCP广场相关API
 */
import axios from 'axios';
import type { McpModuleInfo, McpToolInfo } from '../types/marketplace';

const API_BASE_URL = '/api';

/**
 * 获取所有MCP模块列表
 */
export async function listModules() {
  const response = await axios.get<McpModuleInfo[]>(`${API_BASE_URL}/marketplace/modules`);
  return response.data;
}

/**
 * 获取指定MCP模块详情
 * @param moduleId - 模块ID
 */
export async function getModule(moduleId: number) {
  const response = await axios.get<McpModuleInfo>(`${API_BASE_URL}/marketplace/modules/${moduleId}`);
  return response.data;
}

/**
 * 获取指定MCP模块的所有工具
 * @param moduleId - 模块ID
 */
export async function getModuleTools(moduleId: number) {
  const response = await axios.get<McpToolInfo[]>(`${API_BASE_URL}/marketplace/modules/${moduleId}/tools`);
  return response.data;
}

/**
 * 获取指定MCP工具详情
 * @param toolId - 工具ID
 */
export async function getTool(toolId: number) {
  const response = await axios.get<McpToolInfo>(`${API_BASE_URL}/marketplace/tools/${toolId}`);
  return response.data;
}

/**
 * 扫描仓库中的MCP模块并更新数据库
 */
export async function scanModules() {
  const response = await axios.post(`${API_BASE_URL}/marketplace/scan`);
  return response.data;
}

/**
 * 测试模块工具
 * @param toolId - 工具ID
 * @param params - 工具参数
 */
export async function testModuleTool(toolId: number, params: any) {
  const response = await axios.post(`${API_BASE_URL}/execute/tool/${toolId}`, params);
  return response.data;
} 