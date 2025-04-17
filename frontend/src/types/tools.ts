// types/tools.ts
export interface ToolParameterInfo {
  type: string;
  default?: string | null;
}

export interface ToolInfo {
  name: string;
  doc: string;
  parameters: Record<string, ToolParameterInfo>;
  return_type: string;
  module: string;
  file_path: string;
  // 可以添加 enabled 状态等
  // enabled?: boolean;
}

export interface ToolContent {
  content: string;
}

export interface ToolCreate {
  path: string; // 文件路径，例如 my_tools/new_tool.py
  content: string;
}

export interface ToolUpdate {
  content: string;
} 