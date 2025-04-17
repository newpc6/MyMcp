import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../api';
import type { ResourceInfo, ResourceContent, ResourceCreate, ResourceUpdate } from '../types/resources';

export const useResourceStore = defineStore('resources', () => {
  const resources = ref<ResourceInfo[]>([]);
  const selectedResourcePath = ref<string>('');
  const selectedResourceContent = ref<string>('');
  const loading = ref<boolean>(false);
  const error = ref<string>('');

  const fetchResources = async () => {
    try {
      loading.value = true;
      const response = await api.get<ResourceInfo[]>('/api/resources');
      resources.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取资源列表失败';
    } finally {
      loading.value = false;
    }
  };

  const fetchResourceContent = async (path: string) => {
    try {
      loading.value = true;
      const response = await api.get<ResourceContent>(`/api/resources/${path}`);
      selectedResourceContent.value = response.data.content;
      selectedResourcePath.value = path;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取资源内容失败';
    } finally {
      loading.value = false;
    }
  };

  const createResource = async (resource: ResourceCreate) => {
    try {
      loading.value = true;
      await api.post('/api/resources', resource);
      await fetchResources();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建资源失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateResource = async (path: string, content: ResourceUpdate) => {
    try {
      loading.value = true;
      await api.put(`/api/resources/${path}`, content);
      await fetchResourceContent(path);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新资源失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteResource = async (path: string) => {
    try {
      loading.value = true;
      await api.delete(`/api/resources/${path}`);
      if (selectedResourcePath.value === path) {
        selectedResourcePath.value = '';
        selectedResourceContent.value = '';
      }
      await fetchResources();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除资源失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    resources,
    selectedResourcePath,
    selectedResourceContent,
    loading,
    error,
    fetchResources,
    fetchResourceContent,
    createResource,
    updateResource,
    deleteResource,
  };
}); 