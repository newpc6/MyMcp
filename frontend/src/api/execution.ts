import api from './index';
import type { ToolCall } from '../types/execution';
const prefix = '/api';
/** 执行MCP工具 */
export const executeTool = async (toolCallData: ToolCall): Promise<{ result: any }> => {
  const response = await api.post(`${prefix}/execute`, toolCallData);
  return response.data.data;
}; 