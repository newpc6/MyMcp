/**
 * 统计相关API
 */
import api from './index';
import type { ApiResponse } from '../types/marketplace';

/**
 * 服务统计数据接口
 */
export interface ServiceStats {
  total_services: number;
  running_services: number;
  stopped_services: number;
  error_services: number;
  updated_at: string;
}

/**
 * 模块排名接口
 */
export interface ModuleRanking {
  module_id: number;
  module_name: string;
  service_count: number;
  user_id: number;
  user_name: string;
  updated_at: string;
}

/**
 * 工具排名接口
 */
export interface ToolRanking {
  tool_name: string;
  call_count: number;
  success_count: number;
  error_count: number;
  avg_execution_time: number;
  last_called_at: string | null;
  updated_at: string;
}

/**
 * 服务调用排名接口
 */
export interface ServiceRanking {
  service_id: string;
  service_name: string;
  module_name: string;
  call_count: number;
  success_count: number;
  error_count: number;
  updated_at: string;
}

/**
 * 排名分页响应接口
 */
export interface RankingPaginationResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * 工具执行记录接口
 */
export interface ToolExecution {
  id: number;
  tool_name: string;
  description: string;
  parameters: any;
  result: any;
  status: string;
  execution_time: number;
  created_at: string;
  service_id?: string;
  module_id?: number;
  service?: {
    id: string;
    name: string;
    description: string;
  };
  module?: {
    id: number;
    name: string;
    description: string;
  };
  creator_name?: string;
}

/**
 * 分页工具执行记录接口
 */
export interface ToolExecutionsResponse {
  items: ToolExecution[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * 获取服务统计数据
 */
export async function getServiceStats(): Promise<ApiResponse<ServiceStats>> {
  const response = await api.get('/api/statistics/services');
  return response.data;
}

/**
 * 获取模块发布排名
 * @param size - 每页返回数量
 * @param page - 页码
 */
export async function getModuleRankings(
  size: number = 10, 
  page: number = 1
): Promise<ApiResponse<RankingPaginationResponse<ModuleRanking>>> {
  const response = await api.get('/api/statistics/modules/rankings', {
    params: { size, page }
  });
  return response.data;
}

/**
 * 获取工具调用排名
 * @param size - 每页返回数量
 * @param page - 页码
 */
export async function getToolRankings(
  size: number = 10,
  page: number = 1
): Promise<ApiResponse<RankingPaginationResponse<ToolRanking>>> {
  const response = await api.get('/api/statistics/tools/rankings', {
    params: { size, page }
  });
  return response.data;
}

/**
 * 获取服务调用排名
 * @param size - 每页返回数量
 * @param page - 页码
 */
export async function getServiceRankings(
  size: number = 10,
  page: number = 1
): Promise<ApiResponse<RankingPaginationResponse<ServiceRanking>>> {
  const response = await api.get('/api/statistics/services/rankings', {
    params: { size, page }
  });
  return response.data;
}

/**
 * 获取工具执行记录
 * @param page - 页码
 * @param size - 每页记录数
 * @param toolName - 工具名称过滤
 */
export async function getToolExecutions(
  page: number = 1,
  size: number = 10,
  toolName?: string
): Promise<ApiResponse<ToolExecutionsResponse>> {
  const params: any = {
    page,
    size
  };
  
  if (toolName) {
    params.tool_name = toolName;
  }
  
  const response = await api.get('/api/statistics/tools/executions', { params });
  return response.data;
}

/**
 * 刷新统计数据
 */
export async function refreshStatistics(): Promise<ApiResponse<{ message: string }>> {
  const response = await api.post('/api/statistics/refresh');
  return response.data;
} 