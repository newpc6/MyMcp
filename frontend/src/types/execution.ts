// types/execution.ts
export interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
} 