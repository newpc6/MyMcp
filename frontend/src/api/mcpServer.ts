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
  const response = await api.put(`${apiPrefix}/service/${id}/params`, configParams)
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
  const response = await api.put(`${apiPrefix}/service/${id}/visibility`, {
    is_public: isPublic
  });
  return response.data;
}