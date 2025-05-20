import api from './index';
import { apiPrefix } from './index';
import type { ToolCall } from '../types/execution';

/** 执行MCP工具 */
export const executeTool = async (toolCallData: ToolCall): Promise<{ result: any }> => {
  const response = await api.post(`${apiPrefix}/execute`, toolCallData);
  return response.data.data;
}; 