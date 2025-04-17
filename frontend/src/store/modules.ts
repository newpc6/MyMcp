import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../api';
import type { ModuleInfo, ModuleContent, ModuleCreate, ModuleUpdate } from '../types/modules';

export const useModuleStore = defineStore('modules', () => {
  const modules = ref<ModuleInfo[]>([]);
  const selectedModulePath = ref<string>('');
  const selectedModuleContent = ref<string>('');
  const loading = ref<boolean>(false);
  const error = ref<string>('');

  const fetchModules = async () => {
    try {
      loading.value = true;
      const response = await api.get<ModuleInfo[]>('/api/modules');
      modules.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取模块列表失败';
    } finally {
      loading.value = false;
    }
  };

  const fetchModuleContent = async (path: string) => {
    try {
      loading.value = true;
      const response = await api.get<ModuleContent>(`/api/modules/${path}`);
      selectedModuleContent.value = response.data.content;
      selectedModulePath.value = path;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取模块内容失败';
    } finally {
      loading.value = false;
    }
  };

  const createModule = async (module: ModuleCreate) => {
    try {
      loading.value = true;
      await api.post('/api/modules', module);
      await fetchModules();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建模块失败';
    } finally {
      loading.value = false;
    }
  };

  const updateModule = async (path: string, content: ModuleUpdate) => {
    try {
      loading.value = true;
      await api.put(`/api/modules/${path}`, content);
      await fetchModuleContent(path);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新模块失败';
    } finally {
      loading.value = false;
    }
  };

  const deleteModule = async (path: string) => {
    try {
      loading.value = true;
      await api.delete(`/api/modules/${path}`);
      if (selectedModulePath.value === path) {
        selectedModulePath.value = '';
        selectedModuleContent.value = '';
      }
      await fetchModules();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除模块失败';
    } finally {
      loading.value = false;
    }
  };

  return {
    modules,
    selectedModulePath,
    selectedModuleContent,
    loading,
    error,
    fetchModules,
    fetchModuleContent,
    createModule,
    updateModule,
    deleteModule,
  };
}); 