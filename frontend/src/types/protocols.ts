// types/protocols.ts
export interface ProtocolInfo {
  path: string; // 协议文件的相对路径
  name: string; // 协议名称
  description: string; // 协议描述
  lastModified: string; // 最后修改时间
}

export interface ProtocolContent {
  content: string; // 协议文件内容
}

export interface ProtocolCreate {
  path: string; // 新协议的相对路径，例如 my_protocol.py
  content: string; // 协议文件内容
}

export interface ProtocolUpdate {
  content: string; // 更新的协议文件内容
}

// MCP服务信息相关类型
export interface McpServiceInfo {
  status: 'running' | 'stopped' | 'error'; // 服务状态
  uptime: string; // 运行时间
  version: string; // 版本
  connectionCount: number; // 连接数
}

export interface McpServiceAction {
  action: 'start' | 'stop' | 'restart'; // 服务操作
}

export interface McpServiceActionResult {
  success: boolean;
  message: string;
} 