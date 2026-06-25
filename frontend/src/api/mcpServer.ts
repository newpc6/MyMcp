import { ApiResponse } from '@/types/mcp_template'
import api from '.'
import { apiPrefix } from './index'

const publishedServiceApiPrefix = `${apiPrefix}/published-service`

/**
 * 更新服务参数
 * @param serviceUuid - 服务UUID
 * @param configParams - 配置参数
 */
export async function updateServiceParams(
  id: number,
  configParams: Record<string, any>
): Promise<
  ApiResponse<{
    message: string
  }>
> {
  const response = await api.put(`${publishedServiceApiPrefix}/${id}/params`, configParams)
  return response.data
}


/**
 * 更新服务可见性状态
 * @param serviceUuid - 服务UUID
 * @param isPublic - 是否公开
 */
export async function updateServiceVisibility(id: number, isPublic: boolean): Promise<
  ApiResponse<{
    is_public: boolean
  }>
> {
  const response = await api.put(`${publishedServiceApiPrefix}/${id}/visibility`, {
    is_public: isPublic
  });
  return response.data;
}
