/**
 * MCP鉴权相关类型定义
 */

export interface McpSecretInfo {
  id: number;
  service_id: number;
  secret_key: string;
  secret_name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  expires_at?: string;
  created_by?: number;
}

export interface McpSecretStatistics {
  secret_id: number;
  service_id: number;
  call_count: number;
  success_count: number;
  error_count: number;
  last_access_at?: string;
  statistics_date: string;
  created_at: string;
  updated_at: string;
}

export interface McpAccessLog {
  id: number;
  service_id: number;
  secret_id?: number;
  secret_name?: string;
  client_ip: string;
  user_agent?: string;
  access_time: string;
  status: 'success' | 'error';
  error_message?: string;
  request_headers?: string | Record<string, any>;
}

export interface McpAuthConfig {
  service_id: number;
  auth_required: boolean;
  auth_mode: 'secret' | 'token' | '';
}

export interface CreateSecretRequest {
  name: string;
  description?: string;
  expires_days?: number;
}

export interface UpdateSecretRequest {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface GetSecretsResponse {
  secrets: McpSecretInfo[];
  total: number;
}

export interface GetSecretStatisticsResponse {
  statistics: {
    total_calls: number;
    success_calls: number;
    error_calls: number;
    success_rate: number;
    daily_stats: Array<{
      date: string;
      calls: number;
      success: number;
      error: number;
    }>;
  };
}

export interface GetAccessLogsResponse {
  logs: McpAccessLog[];
  total: number;
}

export interface CreateSecretResponse {
  secret: McpSecretInfo;
  secret_key: string;
  message: string;
}

export interface GetAccessLogsParams {
  secret_id?: number;
  status?: 'success' | 'error';
  page?: number;
  page_size?: number;
  limit?: number;
} 