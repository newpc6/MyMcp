/**
 * MCP广场相关类型定义
 */

/**
 * MCP模块信息
 */
export interface McpModuleInfo {
  id: number;
  name: string;
  description: string;
  module_path: string;
  author?: string;
  version?: string;
  tags: string[] | string;
  icon?: string;
  is_hosted: boolean;
  repository_url?: string;
  created_at: string;
  updated_at: string;
  tools_count: number;
  category_id?: number;
  category_name?: string;
  code?: string;
  user_id?: number;
  creator_name?: string;
  is_public?: boolean;
  markdown_docs?: string;
}

/**
 * API响应类型
 */
export interface ApiResponse<T> {
  code: number;
  data: T;
  message?: string;
  success?: boolean;
}

/**
 * MCP工具参数
 */
export interface McpToolParameter {
  name: string;
  required: boolean;
  type: string;
  default?: any;
}

/**
 * MCP工具信息
 */
export interface McpToolInfo {
  id: number | null;
  module_id: number;
  name: string;
  function_name: string;
  description: string;
  parameters: McpToolParameter[];
  return_type?: string;
  sample_usage?: string;
  created_at?: string;
  updated_at?: string;
  is_enabled: boolean;
  module_name?: string;
}

/**
 * MCP服务信息
 */
export interface McpServiceInfo {
  id: number;
  module_id: number;
  module_name?: string;  // 模块名称
  description?: string;  // 服务描述
  service_uuid: string;
  status: string;
  sse_url: string;
  port?: number;
  user_id?: number | null;
  user_name?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * MCP分组信息
 */
export interface McpCategoryInfo {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  order: number;
  created_at: string;
  updated_at: string;
  modules_count: number;
}

/**
 * 扫描结果
 */
export interface ScanResult {
  new_modules: number;
  new_tools: number;
} 