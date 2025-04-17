<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">MCP 资源管理</h1>

    <div v-if="resourceStore.loading" class="text-center text-gray-500">
      加载中...
    </div>
    <div v-else-if="resourceStore.error" class="text-red-500 bg-red-100 border border-red-400 rounded p-3 mb-4">
      加载错误: {{ resourceStore.error }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- 资源列表 -->
      <div class="md:col-span-1 bg-white p-4 rounded shadow">
        <div class="flex justify-between items-center mb-3">
          <h2 class="text-lg font-semibold">资源列表</h2>
          <button
            @click="showCreateModal = true"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded text-sm"
          >
            新建资源
          </button>
        </div>
        <ul v-if="resourceStore.resources && resourceStore.resources.length > 0" class="space-y-2">
          <li
            v-for="resource in resourceStore.resources"
            :key="resource.path"
            @click="selectResource(resource.path)"
            :class="[
              'p-2 rounded cursor-pointer hover:bg-gray-100 border',
              resourceStore.selectedResourcePath === resource.path ? 'bg-blue-100 border-blue-300' : 'border-transparent'
            ]"
          >
            <span class="font-medium">{{ resource.name }}</span>
            <span class="text-xs text-gray-500 block">({{ resource.path }})</span>
          </li>
        </ul>
        <p v-else class="text-gray-500">没有找到资源。</p>
      </div>

      <!-- 资源详情/编辑器 -->
      <div class="md:col-span-2 bg-white p-4 rounded shadow">
        <div v-if="resourceStore.selectedResourcePath">
          <h2 class="text-lg font-semibold mb-2">编辑资源: {{ resourceStore.selectedResourcePath }}</h2>
          <div v-if="resourceStore.loading && !resourceStore.selectedResourceContent" class="text-gray-500">加载内容...</div>
          <div v-else-if="resourceStore.error && !resourceStore.selectedResourceContent" class="text-red-500">加载内容失败</div>
          <div v-else>
            <textarea
              v-model="editableContent"
              rows="20"
              class="w-full p-2 border rounded font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="资源内容..."
            ></textarea>
            <div class="mt-3 flex justify-end space-x-2">
              <button
                @click="saveResourceChanges"
                :disabled="!isContentChanged || resourceStore.loading"
                class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                保存更改
              </button>
              <button
                @click="confirmDeleteResource"
                :disabled="resourceStore.loading"
                class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                删除资源
              </button>
            </div>
          </div>
        </div>
        <div v-else class="text-center text-gray-500 h-full flex items-center justify-center">
          <p>请从左侧选择一个资源进行编辑。</p>
        </div>
      </div>
    </div>

    <!-- 新建资源 Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
      <div class="relative mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">创建新资源</h3>
        <form @submit.prevent="handleCreateResource">
          <div class="mb-4">
            <label for="newResourcePath" class="block text-sm font-medium text-gray-700">文件路径 (例如: my_resources/resource.json)</label>
            <input
              type="text"
              id="newResourcePath"
              v-model="newResource.path"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div class="mb-4">
            <label for="newResourceContent" class="block text-sm font-medium text-gray-700">初始内容</label>
            <textarea
              id="newResourceContent"
              v-model="newResource.content"
              rows="10"
              required
              class="mt-1 block w-full p-2 border rounded font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="资源内容 (JSON, 文本等)"
            ></textarea>
          </div>
          <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
            <button
              type="submit"
              :disabled="resourceStore.loading"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:col-start-2 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              创建
            </button>
            <button
              type="button"
              @click="showCreateModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm"
            >
              取消
            </button>
          </div>
        </form>
        <p v-if="createError" class="text-red-500 text-sm mt-2">{{ createError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useResourceStore } from '../../store/resources';
import type { ResourceCreate } from '../../types/resources';

const resourceStore = useResourceStore();

const editableContent = ref('');
const showCreateModal = ref(false);
const newResource = ref<ResourceCreate>({ path: '', content: '' });
const createError = ref<string | null>(null);

// 获取资源列表
onMounted(() => {
  resourceStore.fetchResources();
});

// 监听选中资源的变化，更新编辑器内容
watch(() => resourceStore.selectedResourceContent, (newContent) => {
  editableContent.value = newContent ?? '';
});

// 计算内容是否有变化
const isContentChanged = computed(() => {
  return editableContent.value !== (resourceStore.selectedResourceContent ?? '');
});

// 选择资源
function selectResource(resourcePath: string) {
  if (resourceStore.selectedResourcePath !== resourcePath) {
    resourceStore.fetchResourceContent(resourcePath);
  }
}

// 保存更改
async function saveResourceChanges() {
  if (!resourceStore.selectedResourcePath || !isContentChanged.value) return;
  try {
    await resourceStore.updateResource(resourceStore.selectedResourcePath, { content: editableContent.value });
    alert('资源已成功更新！');
  } catch (err) {
    alert(`更新失败: ${resourceStore.error}`);
  }
}

// 处理创建资源
async function handleCreateResource() {
  createError.value = null;
  try {
    await resourceStore.createResource(newResource.value);
    showCreateModal.value = false;
    newResource.value = { path: '', content: '' };
    alert('资源已成功创建！');
  } catch (err) {
    createError.value = resourceStore.error ?? '创建资源时发生未知错误';
  }
}

// 确认删除
async function confirmDeleteResource() {
  if (!resourceStore.selectedResourcePath) return;
  if (confirm(`确定要删除资源 ${resourceStore.selectedResourcePath} 吗？此操作不可恢复！`)) {
    try {
      await resourceStore.deleteResource(resourceStore.selectedResourcePath);
      alert('资源已成功删除！');
    } catch (err) {
      alert(`删除失败: ${resourceStore.error}`);
    }
  }
}
</script>

<style scoped>
/* 可以添加一些特定的样式 */
</style> 