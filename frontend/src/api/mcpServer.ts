import { ApiResponse } from '@/types/marketplace'
import api from '.'
import { apiPrefix } from './index'

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
  const response = await api.put(`${apiPrefix}/mcp/service/${id}/params`, configParams)
  return response.data
}
