import api from './index';
import { apiPrefix } from './index';
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { ApiResponse, McpServiceInfo } from '@/types/marketplace';

/**
 * 获取MCP服务状态
 */
export async function getMcpStatus() {
  const response = await api.get(`${apiPrefix}/service/status`);
  return response.data;
}

/**
 * 获取启用的工具列表
 */
export async function getEnabledTools() {
  const response = await api.get(`${apiPrefix}/service/enabled_tools`);
  return response.data;
}

/**
 * 重启MCP服务
 */
export async function restartMcpService() {
  const response = await api.post(`${apiPrefix}/service/restart`);
  return response.data;
}

/**
 * 加载工具
 * @param modulePath 模块路径
 * @param functionName 函数名称
 * @param toolName 工具名称（可选）
 * @param description 工具描述（可选）
 */
export async function loadTool(
  modulePath: string,
  functionName: string,
  toolName?: string,
  description?: string
) {
  const response = await api.post(`${apiPrefix}/service/load_tool`, {
    module_path: modulePath,
    function_name: functionName,
    tool_name: toolName,
    description: description
  });
  return response.data;
}

/**
 * 获取模块的服务列表
 * @param moduleId - 可选的模块ID
 */
export async function listServices(moduleId?: number): Promise<ApiResponse<McpServiceInfo[]>> {
  let url = `${apiPrefix}/service/list`
  if (moduleId) {
    url += `?module_id=${moduleId}`
  }
  const response = await api.get(url)
  return response.data
}

/**
 * 卸载工具
 * @param toolName 工具名称
 */
export async function unloadTool(toolName: string) {
  const response = await api.post(`${apiPrefix}/service/unload_tool`, {
    tool_name: toolName
  });
  return response.data;
}

/**
 * 更新MCP SSE URL
 * @param sseUrl 新的SSE URL
 */
export async function updateSseUrl(sseUrl: string) {
  const response = await api.put(`${apiPrefix}/service/sse_url`, {
    sse_url: sseUrl
  });
  return response.data;
}

/**
 * 连接到MCP SSE服务
 * @param sseUrl SSE URL
 */
export async function connectToMcpSse(sseUrl: string) {
  try {
    // 获取用户信息，添加认证头
    let headers: HeadersInit = {
      Accept: "text/event-stream",
    };

    // 从localStorage获取token
    const userInfoStr = localStorage.getItem('userInfo');
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr);
        if (userInfo && userInfo.token) {
          headers['Authorization'] = `Bearer ${userInfo.token}`;
        }
      } catch (e) {
        console.error('解析用户信息失败', e);
      }
    }

    const transport = new SSEClientTransport(new URL(sseUrl), {
      eventSourceInit: {
        fetch: (url, init) => fetch(url, { ...init, headers }),
      },
      requestInit: {
        headers,
      },
    });

    await transport.start();
    return {
      success: true,
      transport,
      message: '成功连接到MCP SSE服务'
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || '连接MCP SSE服务失败',
      details: error
    };
  }
}

/**
 * 测试MCP SSE连接
 * @param sseUrl SSE URL
 */
export async function testMcpSseConnection(sseUrl: string) {
  try {
    const connection = await connectToMcpSse(sseUrl);

    // 如果连接成功，立即关闭
    if (connection.success && connection.transport) {
      await connection.transport.close();
    }

    return {
      success: connection.success,
      message: connection.success ? '连接测试成功' : connection.error
    };
  } catch (error: any) {
    return {
      success: false,
      message: error.message || '连接测试失败'
    };
  }
} 