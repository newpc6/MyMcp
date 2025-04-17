import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { ToolInfo, ToolContent, ToolCreate, ToolUpdate } from '../types/tools';
import {
  getTools as apiGetTools,
  getToolContent as apiGetToolContent,
  createTool as apiCreateTool,
  updateTool as apiUpdateTool,
  deleteTool as apiDeleteTool,
  // listTools as apiListTools, // 暂时不用，getTools已包含信息
  // getToolInfo as apiGetToolInfo, // 暂时不用，getTools已包含信息
} from '../api/tools';

export const useToolStore = defineStore('tools', () => {
  // State
  const tools = ref<ToolInfo[]>([]);
  const currentToolContent = ref<ToolContent | null>(null);
  const currentToolPath = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const toolList = computed(() => tools.value);
  const selectedToolContent = computed(() => currentToolContent.value?.content);
  const selectedToolPath = computed(() => currentToolPath.value);

  // Actions
  async function fetchTools() {
    isLoading.value = true;
    error.value = null;
    try {
      tools.value = await apiGetTools();
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch tools';
      tools.value = []; // 清空以防显示旧数据
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchToolContent(toolPath: string) {
    isLoading.value = true;
    error.value = null;
    currentToolContent.value = null; // 清空旧内容
    currentToolPath.value = toolPath;
    try {
      currentToolContent.value = await apiGetToolContent(toolPath);
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch tool content';
    } finally {
      isLoading.value = false;
    }
  }

  async function createTool(toolData: ToolCreate) {
    isLoading.value = true;
    error.value = null;
    try {
      await apiCreateTool(toolData);
      // 创建成功后刷新列表
      await fetchTools();
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to create tool';
      throw err; // 将错误抛出给调用者处理 UI 反馈
    } finally {
      isLoading.value = false;
    }
  }

  async function updateTool(toolPath: string, toolData: ToolUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      await apiUpdateTool(toolPath, toolData);
      // 如果更新的是当前选中的工具，则刷新其内容
      if (currentToolPath.value === toolPath) {
        await fetchToolContent(toolPath);
      }
      // 可以考虑只更新 tools.value 中对应项的 doc (如果 ToolUpdate 返回了新信息)
      // 否则，简单刷新列表可能更直接
      await fetchTools();
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to update tool';
      throw err; // 将错误抛出给调用者处理 UI 反馈
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteTool(toolPath: string) {
    isLoading.value = true;
    error.value = null;
    try {
      await apiDeleteTool(toolPath);
      // 删除成功后刷新列表
      await fetchTools();
      // 如果删除的是当前选中的工具，清空内容
      if (currentToolPath.value === toolPath) {
        currentToolContent.value = null;
        currentToolPath.value = null;
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to delete tool';
      throw err; // 将错误抛出给调用者处理 UI 反馈
    } finally {
      isLoading.value = false;
    }
  }

  function clearSelection() {
    currentToolContent.value = null;
    currentToolPath.value = null;
    error.value = null;
  }

  return {
    // State refs
    // tools, // 不直接暴露 state，通过 getter 访问
    // currentToolContent,
    // currentToolPath,
    isLoading,
    error,

    // Getters
    toolList,
    selectedToolContent,
    selectedToolPath,

    // Actions
    fetchTools,
    fetchToolContent,
    createTool,
    updateTool,
    deleteTool,
    clearSelection,
  };
}); 