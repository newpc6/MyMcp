/**
 * MCP广场相关API
 */
import api from './index'
import type { McpModuleInfo, McpToolInfo, ScanResult, McpCategoryInfo, McpServiceInfo, ApiResponse } from '../types/marketplace'

/**
 * 获取所有MCP模块列表
 */
export async function listModules(categoryId?: string | null): Promise<ApiResponse<McpModuleInfo[]>> {
  let url = '/api/marketplace/modules'
  if (categoryId) {
    url += `?category_id=${categoryId}`
  }
  const response = await api.get(url)
  return response.data
}

/**
 * 获取指定MCP模块详情
 * @param moduleId - 模块ID
 */
export async function getModule(moduleId: number): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.get(`/api/marketplace/modules/${moduleId}`)
  return response.data
}

/**
 * 创建MCP模块/服务
 * @param data - 模块数据
 */
export async function createModule(data: Partial<McpModuleInfo>): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.post('/api/marketplace/modules', data)
  return response.data
}

/**
 * 获取指定MCP模块的所有工具
 * @param moduleId - 模块ID
 */
export async function getModuleTools(moduleId: number): Promise<ApiResponse<McpToolInfo[]>> {
  const response = await api.get(`/api/marketplace/modules/${moduleId}/tools`)
  return response.data
}

/**
 * 获取指定MCP工具详情
 * @param toolId - 工具ID
 */
export async function getTool(toolId: number): Promise<ApiResponse<McpToolInfo>> {
  const response = await api.get(`/api/marketplace/tools/${toolId}`)
  return response.data
}

/**
 * 扫描仓库中的MCP模块并更新数据库
 */
export async function scanModules(): Promise<ApiResponse<ScanResult>> {
  const response = await api.post('/api/marketplace/modules/scan')
  return response.data
}

/**
 * 获取所有MCP分组
 */
export async function listCategories(): Promise<ApiResponse<McpCategoryInfo[]>> {
  const response = await api.get('/api/marketplace/categories')
  return response.data
}

/**
 * 获取分组详情
 */
export async function getCategory(categoryId: number): Promise<ApiResponse<McpCategoryInfo>> {
  const response = await api.get(`/api/marketplace/categories/${categoryId}`)
  return response.data
}

/**
 * 创建MCP分组
 */
export async function createCategory(data: Partial<McpCategoryInfo>): Promise<ApiResponse<McpCategoryInfo>> {
  const response = await api.post('/api/marketplace/categories', data)
  return response.data
}

/**
 * 更新MCP分组
 */
export async function updateCategory(categoryId: number, data: Partial<McpCategoryInfo>): Promise<ApiResponse<McpCategoryInfo>> {
  const response = await api.put(`/api/marketplace/categories/${categoryId}`, data)
  return response.data
}

/**
 * 删除MCP分组
 */
export async function deleteCategory(categoryId: number): Promise<ApiResponse<boolean>> {
  const response = await api.delete(`/api/marketplace/categories/${categoryId}`)
  return response.data
}

/**
 * 更新模块所属分组
 */
export async function updateModuleCategory(moduleId: number, categoryId: number | null): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.put(`/api/marketplace/modules/${moduleId}/category`, { category_id: categoryId })
  return response.data
}

/**
 * 更新模块信息
 * @param moduleId - 模块ID
 * @param data - 要更新的模块数据
 */
export async function updateModule(moduleId: number, data: Partial<McpModuleInfo>): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.put(`/api/marketplace/modules/${moduleId}`, data)
  return response.data
}

/**
 * 测试模块工具
 * @param toolId - 工具ID
 * @param params - 工具参数
 */
export async function testModuleTool(toolId: number, params: any): Promise<ApiResponse<any>> {
  const response = await api.post(`/api/execute/tool/${toolId}`, params)
  return response.data
}

/**
 * 测试模块工具(通过模块ID和函数名)
 * @param moduleId - 模块ID
 * @param functionName - 函数名称
 * @param params - 工具参数
 */
export async function testModuleFunction(moduleId: number, functionName: string, params: any): Promise<ApiResponse<any>> {
  const response = await api.post(`/api/execute/module/${moduleId}/function/${functionName}`, params)
  return response.data
}

/**
 * 获取模块的服务列表
 * @param moduleId - 可选的模块ID
 */
export async function listServices(moduleId?: number): Promise<ApiResponse<McpServiceInfo[]>> {
  let url = '/api/marketplace/services'
  if (moduleId) {
    url += `?module_id=${moduleId}`
  }
  const response = await api.get(url)
  return response.data
}

/**
 * 发布模块
 * @param moduleId - 模块ID
 * @param configParams - 配置参数，可选
 */
export async function publishModule(
  moduleId: number,
  configParams?: Record<string, any>
): Promise<
  ApiResponse<{
    message: string
    service: McpServiceInfo
  }>
> {
  const response = await api.post(`/api/marketplace/modules/${moduleId}/publish`, configParams || {})
  return response.data
}

/**
 * 停止服务
 * @param serviceUuid - 服务UUID
 */
export async function stopService(serviceUuid: string): Promise<
  ApiResponse<{
    message: string
  }>
> {
  const response = await api.post(`/api/marketplace/services/${serviceUuid}/stop`)
  return response.data
}

/**
 * 启动服务
 * @param serviceUuid - 服务UUID
 */
export async function startService(serviceUuid: string): Promise<
  ApiResponse<{
    message: string
  }>
> {
  const response = await api.post(`/api/marketplace/services/${serviceUuid}/start`)
  return response.data
}

/**
 * 卸载服务（删除数据库记录并停止服务）
 * @param serviceUuid - 服务UUID
 */
export async function uninstallService(serviceUuid: string): Promise<
  ApiResponse<{
    message: string
  }>
> {
  const response = await api.post(`/api/marketplace/services/${serviceUuid}/uninstall`)
  return response.data
}

/**
 * 删除MCP模块
 * @param moduleId - 模块ID
 */
export async function deleteModule(moduleId: number): Promise<ApiResponse<{ message: string }>> {
  const response = await api.delete(`/api/marketplace/modules/${moduleId}`)
  return response.data
}

/**
 * 获取服务详情
 * @param serviceUuid - 服务UUID
 */
export async function getService(serviceUuid: string): Promise<ApiResponse<McpServiceInfo>> {
  const response = await api.get(`/api/marketplace/services/${serviceUuid}`)
  return response.data
}

/**
 * 获取MCP服务状态
 */
export async function getOnlineServices(): Promise<ApiResponse<string[]>> {
  const response = await api.get(`/api/marketplace/services/online`)
  return response.data
}

/**
 * 更新服务参数
 * @param serviceUuid - 服务UUID
 * @param configParams - 配置参数
 */
export async function updateServiceParams(
  serviceUuid: string,
  configParams: Record<string, any>
): Promise<
  ApiResponse<{
    message: string
    service: McpServiceInfo
  }>
> {
  const response = await api.put(`/api/marketplace/services/${serviceUuid}/params`, configParams)
  return response.data
}
