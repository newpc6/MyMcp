/**
 * MCP广场相关API
 */
import httpClient from '../utils/http-client';
import type { McpModuleInfo, McpToolInfo, ScanResult, McpCategoryInfo } from '../types/marketplace';

/**
 * 获取所有MCP模块列表
 */
export async function listModules(categoryId?: string | null): Promise<McpModuleInfo[]> {
  let url = '/api/marketplace/modules';
  if (categoryId) {
    url += `?category_id=${categoryId}`;
  }
  const response = await httpClient.get(url);
  return response.data;
}

/**
 * 获取指定MCP模块详情
 * @param moduleId - 模块ID
 */
export async function getModule(moduleId: number): Promise<McpModuleInfo> {
  const response = await httpClient.get(`/api/marketplace/modules/${moduleId}`);
  return response.data;
}

/**
 * 获取指定MCP模块的所有工具
 * @param moduleId - 模块ID
 */
export async function getModuleTools(moduleId: number): Promise<McpToolInfo[]> {
  const response = await httpClient.get(`/api/marketplace/modules/${moduleId}/tools`);
  return response.data;
}

/**
 * 获取指定MCP工具详情
 * @param toolId - 工具ID
 */
export async function getTool(toolId: number): Promise<McpToolInfo> {
  const response = await httpClient.get(`/api/marketplace/tools/${toolId}`);
  return response.data;
}

/**
 * 扫描仓库中的MCP模块并更新数据库
 */
export async function scanModules(): Promise<ScanResult> {
  const response = await httpClient.post('/api/marketplace/scan');
  return response.data;
}

/**
 * 获取所有MCP分组
 */
export async function listCategories(): Promise<McpCategoryInfo[]> {
  const response = await httpClient.get('/api/marketplace/categories');
  return response.data;
}

/**
 * 获取分组详情
 */
export async function getCategory(categoryId: number): Promise<McpCategoryInfo> {
  const response = await httpClient.get(`/api/marketplace/categories/${categoryId}`);
  return response.data;
}

/**
 * 创建MCP分组
 */
export async function createCategory(data: Partial<McpCategoryInfo>): Promise<McpCategoryInfo> {
  const response = await httpClient.post('/api/marketplace/categories', data);
  return response.data;
}

/**
 * 更新MCP分组
 */
export async function updateCategory(categoryId: number, data: Partial<McpCategoryInfo>): Promise<McpCategoryInfo> {
  const response = await httpClient.put(`/api/marketplace/categories/${categoryId}`, data);
  return response.data;
}

/**
 * 删除MCP分组
 */
export async function deleteCategory(categoryId: number): Promise<boolean> {
  const response = await httpClient.delete(`/api/marketplace/categories/${categoryId}`);
  return response.data.success;
}

/**
 * 更新模块所属分组
 */
export async function updateModuleCategory(moduleId: number, categoryId: number | null): Promise<McpModuleInfo> {
  const response = await httpClient.put(`/api/marketplace/modules/${moduleId}/category`, { category_id: categoryId });
  return response.data;
}

/**
 * 更新模块信息
 * @param moduleId - 模块ID
 * @param data - 要更新的模块数据
 */
export async function updateModule(moduleId: number, data: Partial<McpModuleInfo>): Promise<McpModuleInfo> {
  const response = await httpClient.put(`/api/marketplace/modules/${moduleId}`, data);
  return response.data;
}

/**
 * 测试模块工具
 * @param toolId - 工具ID
 * @param params - 工具参数
 */
export async function testModuleTool(toolId: number, params: any) {
  const response = await httpClient.post(`/api/execute/tool/${toolId}`, params);
  return response.data;
}

/**
 * 测试模块工具(通过模块ID和函数名)
 * @param moduleId - 模块ID
 * @param functionName - 函数名称
 * @param params - 工具参数
 */
export async function testModuleFunction(moduleId: number, functionName: string, params: any) {
  const response = await httpClient.post(`/api/execute/module/${moduleId}/function/${functionName}`, params);
  return response.data;
} 