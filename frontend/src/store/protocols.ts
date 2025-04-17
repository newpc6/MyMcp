import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../api';
import type { 
  ProtocolInfo, 
  ProtocolContent, 
  ProtocolCreate, 
  ProtocolUpdate,
  McpServiceInfo,
  McpServiceAction,
  McpServiceActionResult
} from '../types/protocols';

export const useProtocolStore = defineStore('protocols', () => {
  const protocols = ref<ProtocolInfo[]>([]);
  const selectedProtocolPath = ref<string>('');
  const selectedProtocolContent = ref<string>('');
  const serviceInfo = ref<McpServiceInfo | null>(null);
  const loading = ref<boolean>(false);
  const error = ref<string>('');

  // 获取所有协议
  const fetchProtocols = async () => {
    try {
      loading.value = true;
      const response = await api.get<ProtocolInfo[]>('/api/protocols');
      protocols.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取协议列表失败';
    } finally {
      loading.value = false;
    }
  };

  // 获取协议内容
  const fetchProtocolContent = async (path: string) => {
    try {
      loading.value = true;
      const response = await api.get<ProtocolContent>(`/api/protocols/${path}`);
      selectedProtocolContent.value = response.data.content;
      selectedProtocolPath.value = path;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取协议内容失败';
    } finally {
      loading.value = false;
    }
  };

  // 创建新协议
  const createProtocol = async (protocol: ProtocolCreate) => {
    try {
      loading.value = true;
      await api.post('/api/protocols', protocol);
      await fetchProtocols();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建协议失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // 更新协议
  const updateProtocol = async (path: string, content: ProtocolUpdate) => {
    try {
      loading.value = true;
      await api.put(`/api/protocols/${path}`, content);
      await fetchProtocolContent(path);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新协议失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // 删除协议
  const deleteProtocol = async (path: string) => {
    try {
      loading.value = true;
      await api.delete(`/api/protocols/${path}`);
      if (selectedProtocolPath.value === path) {
        selectedProtocolPath.value = '';
        selectedProtocolContent.value = '';
      }
      await fetchProtocols();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除协议失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // 获取MCP服务信息
  const fetchServiceInfo = async () => {
    try {
      loading.value = true;
      const response = await api.get<McpServiceInfo>('/api/mcp/service');
      serviceInfo.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取MCP服务信息失败';
    } finally {
      loading.value = false;
    }
  };

  // 控制MCP服务（启动、停止、重启）
  const controlService = async (action: McpServiceAction) => {
    try {
      loading.value = true;
      const response = await api.post<McpServiceActionResult>('/api/mcp/service', action);
      await fetchServiceInfo();
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : `${action.action}MCP服务失败`;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    protocols,
    selectedProtocolPath,
    selectedProtocolContent,
    serviceInfo,
    loading,
    error,
    fetchProtocols,
    fetchProtocolContent,
    createProtocol,
    updateProtocol,
    deleteProtocol,
    fetchServiceInfo,
    controlService,
  };
}); 