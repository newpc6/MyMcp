/**
 * MCP鉴权相关API
 */
import api from './index'
import { apiPrefix } from './index'
import type { ApiResponse } from '../types/marketplace'
import type {
    McpSecretInfo,
    McpSecretStatistics,
    McpAccessLog,
    McpAuthConfig,
    CreateSecretRequest,
    UpdateSecretRequest,
    GetSecretsResponse,
    GetSecretStatisticsResponse,
    GetAccessLogsResponse,
    CreateSecretResponse,
    GetAccessLogsParams
} from '../types/mcp-auth'
import { Page } from '@/types/page'

/**
 * 创建密钥
 * @param serviceId - 服务ID
 * @param data - 密钥创建数据
 */
export async function createSecret(
    serviceId: number,
    data: CreateSecretRequest
): Promise<ApiResponse<CreateSecretResponse>> {
    const response = await api.post(`${apiPrefix}/mcp-auth/services/${serviceId}/secrets`, data)
    return response.data
}

/**
 * 获取密钥列表
 * @param serviceId - 服务ID
 */
export async function getSecrets(serviceId: number): Promise<ApiResponse<GetSecretsResponse>> {
    const response = await api.get(`${apiPrefix}/mcp-auth/services/${serviceId}/secrets`)
    return response.data
}

/**
 * 更新密钥
 * @param secretId - 密钥ID
 * @param data - 更新数据
 */
export async function updateSecret(
    secretId: number,
    data: UpdateSecretRequest
): Promise<ApiResponse<McpSecretInfo>> {
    const response = await api.put(`${apiPrefix}/mcp-auth/secrets/${secretId}`, data)
    return response.data
}

/**
 * 删除密钥
 * @param secretId - 密钥ID
 */
export async function deleteSecret(secretId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete(`${apiPrefix}/mcp-auth/secrets/${secretId}`)
    return response.data
}

/**
 * 获取密钥统计信息
 * @param secretId - 密钥ID
 * @param days - 统计天数，默认30天
 */
export async function getSecretStatistics(
    secretId: number,
    days: number = 30
): Promise<ApiResponse<GetSecretStatisticsResponse>> {
    const response = await api.get(`${apiPrefix}/mcp-auth/secrets/${secretId}/statistics`, {
        params: { days }
    })
    return response.data
}

/**
 * 获取密钥信息
 * @param secretId - 密钥ID
 */
export async function getSecretInfo(serviceId: number): Promise<ApiResponse<McpSecretInfo>> {
    const response = await api.get(`${apiPrefix}/mcp-auth/services/${serviceId}/secrets-info`)
    return response.data
}

/**
 * 获取访问日志
 * @param serviceId - 服务ID
 * @param params - 查询参数
 */
export async function getAccessLogs(
    serviceId: number,
    params: Page
): Promise<ApiResponse<GetAccessLogsResponse>> {
    const response = await api.post(`${apiPrefix}/mcp-auth/services/${serviceId}/access-logs`,
        params
    )
    return response.data
}

/**
 * 获取鉴权配置
 * @param serviceId - 服务ID
 */
export async function getAuthConfig(serviceId: number): Promise<ApiResponse<McpAuthConfig>> {
    const response = await api.get(`${apiPrefix}/mcp-auth/services/${serviceId}/auth-config`)
    return response.data
}

/**
 * 更新鉴权配置
 * @param serviceId - 服务ID
 * @param data - 配置数据
 */
export async function updateAuthConfig(
    serviceId: number,
    data: Partial<McpAuthConfig>
): Promise<ApiResponse<McpAuthConfig>> {
    const response = await api.put(`${apiPrefix}/mcp-auth/services/${serviceId}/auth-config`, data)
    return response.data
}

// 为了兼容性，导出一个包含所有方法的对象
export const mcpAuthApi = {
    createSecret,
    getSecrets,
    updateSecret,
    deleteSecret,
    getSecretStatistics,
    getAccessLogs,
    getAuthConfig,
    updateAuthConfig,
    getSecretInfo
}

export default mcpAuthApi 