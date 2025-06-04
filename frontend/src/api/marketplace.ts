/**
 * MCP广场相关API
 */
import api from './index'
import { apiPrefix } from './index'
import type { McpModuleInfo, McpToolInfo, ScanResult, McpCategoryInfo, McpServiceInfo, ApiResponse } from '../types/marketplace'
import { Page } from '@/types/page';


export async function pageModules(params: Page) {
  const response = await api.post(`${apiPrefix}/marketplace/modules/page`, params);
  return response.data;
}

/**
 * 获取MCP模块列表（支持分页）
 */
export async function listModules() {
  let url = `${apiPrefix}/marketplace/modules`
  const params = new URLSearchParams()

  if (params.toString()) {
    url += `?${params.toString()}`
  }

  const response = await api.get(url)
  return response.data
}

/**
 * 获取指定MCP模块详情
 * @param moduleId - 模块ID
 */
export async function getModule(moduleId: number): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.get(`${apiPrefix}/marketplace/modules/${moduleId}`)
  return response.data
}

/**
 * 创建MCP模块/服务
 * @param data - 模块数据
 */
export async function createModule(data: Partial<McpModuleInfo>): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.post(`${apiPrefix}/marketplace/modules`, data)
  return response.data
}

/**
 * 获取指定MCP模块的所有工具
 * @param moduleId - 模块ID
 */
export async function getModuleTools(moduleId: number): Promise<ApiResponse<McpToolInfo[]>> {
  const response = await api.get(`${apiPrefix}/marketplace/modules/${moduleId}/tools`)
  return response.data
}

/**
 * 获取指定MCP工具详情
 * @param toolId - 工具ID
 */
export async function getTool(toolId: number): Promise<ApiResponse<McpToolInfo>> {
  const response = await api.get(`${apiPrefix}/marketplace/tools/${toolId}`)
  return response.data
}

/**
 * 扫描仓库中的MCP模块并更新数据库
 */
export async function scanModules(): Promise<ApiResponse<ScanResult>> {
  const response = await api.post(`${apiPrefix}/marketplace/modules/scan`)
  return response.data
}

/**
 * 获取所有MCP分组
 */
export async function listGroup(): Promise<ApiResponse<McpCategoryInfo[]>> {
  const response = await api.get(`${apiPrefix}/group`)
  return response.data
}

/**
 * 获取分组详情
 */
export async function getGroup(groupId: number): Promise<ApiResponse<McpCategoryInfo>> {
  const response = await api.get(`${apiPrefix}/group/${groupId}`)
  return response.data
}

/**
 * 创建MCP分类
 * @param categoryData 分类数据
 * @returns 
 */
export const createGroup = (groupData: any) => {
  return api.post(`${apiPrefix}/group`, groupData)
}

/**
 * 更新MCP分类
 * @param categoryId 分类ID
 * @param categoryData 分类数据
 * @returns 
 */
export const updateGroup = (groupId: number, groupData: any) => {
  return api.put(`${apiPrefix}/group/${groupId}`, groupData)
}

/**
 * 删除MCP分类
 * @param categoryId 分类ID
 * @returns 
 */
export async function deleteGroup(groupId: number) {
  return await api.delete(`${apiPrefix}/group/${groupId}`)
}

/**
 * 更新模块所属分组
 */
export async function updateModuleGroup(moduleId: number, groupId: number | null): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.put(`${apiPrefix}/modules/${moduleId}/group`, { group_id: groupId })
  return response.data
}

/**
 * 更新模块信息
 * @param moduleId - 模块ID
 * @param data - 要更新的模块数据
 */
export async function updateModule(moduleId: number, data: Partial<McpModuleInfo>): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.put(`${apiPrefix}/marketplace/modules/${moduleId}`, data)
  return response.data
}

/**
 * 测试模块工具
 * @param toolId - 工具ID
 * @param params - 工具参数
 */
export async function testModuleTool(toolId: number, params: any): Promise<ApiResponse<any>> {
  const response = await api.post(`${apiPrefix}/execute/tool/${toolId}`, params)
  return response.data
}

/**
 * 测试模块工具(通过模块ID和函数名)
 * @param moduleId - 模块ID
 * @param functionName - 函数名称
 * @param params - 工具参数
 * @param configParams - 配置参数（可选）
 */
export async function testModuleFunction(
  moduleId: number, 
  functionName: string, 
  params: any, 
  configParams?: Record<string, any>
): Promise<ApiResponse<any>> {
  const requestData = {
    ...params,
    ...(configParams && { _config_params: configParams })
  };
  const response = await api.post(`${apiPrefix}/execute/module/${moduleId}/function/${functionName}`, requestData)
  return response.data
}

/**
 * 获取模块的服务列表
 * @param moduleId - 可选的模块ID
 */
export async function listServices(moduleId?: number): Promise<ApiResponse<McpServiceInfo[]>> {
  let url = `${apiPrefix}/service/list`
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
  const response = await api.post(`${apiPrefix}/marketplace/modules/${moduleId}/publish`, configParams || {})
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
  const response = await api.post(`${apiPrefix}/service/${serviceUuid}/stop`)
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
  const response = await api.post(`${apiPrefix}/service/${serviceUuid}/start`)
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
  const response = await api.post(`${apiPrefix}/service/${serviceUuid}/uninstall`)
  return response.data
}

/**
 * 删除MCP模块
 * @param moduleId - 模块ID
 */
export async function deleteModule(moduleId: number): Promise<ApiResponse<{ message: string }>> {
  const response = await api.delete(`${apiPrefix}/marketplace/modules/${moduleId}`)
  return response.data
}

/**
 * 获取服务详情
 * @param serviceUuid - 服务UUID
 */
export async function getService(serviceUuid: string): Promise<ApiResponse<McpServiceInfo>> {
  const response = await api.get(`${apiPrefix}/service/${serviceUuid}`)
  return response.data
}

/**
 * 获取MCP服务状态
 */
export async function getOnlineServices(): Promise<ApiResponse<string[]>> {
  const response = await api.get(`${apiPrefix}/service/online`)
  return response.data
}

/**
 * 复制MCP模块
 * @param moduleId - 源模块ID
 * @param data - 新模块的自定义数据
 */
export async function cloneModule(moduleId: number, data: Partial<McpModuleInfo>): Promise<ApiResponse<McpModuleInfo>> {
  const response = await api.post(`${apiPrefix}/marketplace/modules/${moduleId}/clone`, data)
  return response.data
}

/**
 * 更新服务参数
 */
// export async function updateServiceParams(serviceId: number, configParams: Record<string, any>) {
//   const response = await api.put(`${apiPrefix}/service/${serviceId}/params`, {
//     config_params: configParams
//   });
//   return response.data;
// }


/**
 * 分页查询服务列表
 */
export async function pageServices(params: Page) {
  const response = await api.post(`${apiPrefix}/service/page`, params);
  return response.data;
}

/**
 * 创建第三方MCP服务
 * @param data - 第三方服务数据
 */
export async function createThirdPartyService(data: {
  service_name: string;
  sse_url: string;
  description?: string;
  is_public?: boolean;
}): Promise<ApiResponse<{
  message: string;
  service: McpServiceInfo;
}>> {
  const response = await api.post(`${apiPrefix}/service/third-party-services`, data);
  return response.data;
}
