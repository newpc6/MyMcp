<template>
  <div class="container mx-auto p-4 bg-gray-900 text-gray-100 min-h-screen">
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-2 text-blue-400">MCP 协议管理</h1>
      <p class="text-gray-400">管理MCP协议文件、查看和控制MCP服务状态</p>
    </div>

    <!-- 服务状态面板 -->
    <div class="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700 shadow-xl">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-blue-300">MCP 服务状态</h2>
        <div class="flex space-x-2">
          <button 
            @click="startService" 
            :disabled="protocolStore.loading || protocolStore.serviceInfo?.status === 'running'"
            class="px-4 py-2 rounded bg-green-600 hover:bg-green-700 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            启动
          </button>
          <button 
            @click="stopService" 
            :disabled="protocolStore.loading || protocolStore.serviceInfo?.status === 'stopped'"
            class="px-4 py-2 rounded bg-red-600 hover:bg-red-700 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            停止
          </button>
          <button 
            @click="restartService" 
            :disabled="protocolStore.loading || protocolStore.serviceInfo?.status === 'stopped'"
            class="px-4 py-2 rounded bg-yellow-600 hover:bg-yellow-700 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            重启
          </button>
        </div>
      </div>

      <div v-if="protocolStore.loading && !protocolStore.serviceInfo" class="mt-4 text-center text-gray-400">
        加载服务信息...
      </div>
      <div v-else-if="protocolStore.error && !protocolStore.serviceInfo" class="mt-4 text-red-400">
        {{ protocolStore.error }}
      </div>
      <div v-else-if="protocolStore.serviceInfo" class="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-gray-700 p-3 rounded-lg border border-gray-600">
          <div class="text-sm text-gray-400">状态</div>
          <div class="font-semibold flex items-center">
            <span 
              :class="{
                'bg-green-500': protocolStore.serviceInfo.status === 'running',
                'bg-red-500': protocolStore.serviceInfo.status === 'stopped',
                'bg-yellow-500': protocolStore.serviceInfo.status === 'error'
              }" 
              class="w-3 h-3 rounded-full mr-2 inline-block"
            ></span>
            {{ protocolStore.serviceInfo.status === 'running' ? '运行中' : 
               protocolStore.serviceInfo.status === 'stopped' ? '已停止' : '错误' }}
          </div>
        </div>
        <div class="bg-gray-700 p-3 rounded-lg border border-gray-600">
          <div class="text-sm text-gray-400">运行时间</div>
          <div class="font-semibold">{{ protocolStore.serviceInfo.uptime }}</div>
        </div>
        <div class="bg-gray-700 p-3 rounded-lg border border-gray-600">
          <div class="text-sm text-gray-400">版本</div>
          <div class="font-semibold">{{ protocolStore.serviceInfo.version }}</div>
        </div>
        <div class="bg-gray-700 p-3 rounded-lg border border-gray-600">
          <div class="text-sm text-gray-400">连接数</div>
          <div class="font-semibold">{{ protocolStore.serviceInfo.connectionCount }}</div>
        </div>
      </div>
    </div>

    <div v-if="protocolStore.loading && !protocolStore.protocols.length" class="text-center text-gray-400">
      加载中...
    </div>
    <div v-else-if="protocolStore.error && !protocolStore.protocols.length" class="text-red-400 bg-red-900 bg-opacity-30 border border-red-800 rounded p-3 mb-4">
      加载错误: {{ protocolStore.error }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 协议列表 -->
      <div class="md:col-span-1 bg-gray-800 p-4 rounded-lg shadow-xl border border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-blue-300">协议列表</h2>
          <button
            @click="showCreateModal = true"
            class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded text-sm transition"
          >
            新建协议
          </button>
        </div>
        <div class="relative">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索协议..." 
            class="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''" 
            class="absolute right-3 top-2 text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>
        <ul v-if="filteredProtocols.length > 0" class="space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar">
          <li
            v-for="protocol in filteredProtocols"
            :key="protocol.path"
            @click="selectProtocol(protocol.path)"
            :class="[
              'p-3 rounded-lg cursor-pointer hover:bg-gray-700 border transition',
              protocolStore.selectedProtocolPath === protocol.path ? 'bg-blue-900 border-blue-600' : 'border-gray-700'
            ]"
          >
            <div class="flex justify-between items-start">
              <span class="font-medium text-blue-300">{{ protocol.name }}</span>
              <span class="text-xs px-2 py-1 bg-gray-700 rounded-full text-gray-300">{{ formatDate(protocol.lastModified) }}</span>
            </div>
            <span class="text-xs text-gray-400 block mt-1">{{ protocol.path }}</span>
            <p v-if="protocol.description" class="text-sm text-gray-300 mt-1 line-clamp-2">{{ protocol.description }}</p>
          </li>
        </ul>
        <div v-else-if="searchQuery" class="text-gray-400 text-center p-4">
          没有找到匹配的协议。
        </div>
        <div v-else class="text-gray-400 text-center p-4">
          没有协议可显示。点击"新建协议"按钮创建。
        </div>
      </div>

      <!-- 协议详情/编辑器 -->
      <div class="md:col-span-2 bg-gray-800 p-4 rounded-lg shadow-xl border border-gray-700">
        <div v-if="protocolStore.selectedProtocolPath">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-blue-300">
              编辑协议: <span class="text-gray-300">{{ getProtocolName() }}</span>
            </h2>
            <div class="text-sm text-gray-400">
              路径: {{ protocolStore.selectedProtocolPath }}
            </div>
          </div>
          <div v-if="protocolStore.loading && !protocolStore.selectedProtocolContent" class="text-gray-400 text-center p-10">
            加载内容中...
          </div>
          <div v-else-if="protocolStore.error && !protocolStore.selectedProtocolContent" class="text-red-400 text-center p-10">
            加载协议内容失败: {{ protocolStore.error }}
          </div>
          <div v-else>
            <textarea
              v-model="editableContent"
              rows="20"
              class="w-full p-3 border rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-900 text-gray-100 border-gray-700 resize-none"
              placeholder="协议代码..."
            ></textarea>
            <div class="mt-4 flex justify-end space-x-3">
              <button
                @click="saveProtocolChanges"
                :disabled="!isContentChanged || protocolStore.loading"
                class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                保存更改
              </button>
              <button
                @click="confirmDeleteProtocol"
                :disabled="protocolStore.loading"
                class="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                删除协议
              </button>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full p-10 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-400 mb-2">请从左侧选择一个协议进行编辑</p>
          <p class="text-gray-500 text-sm">或点击"新建协议"按钮创建一个新的协议</p>
        </div>
      </div>
    </div>

    <!-- 新建协议 Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-75 overflow-y-auto h-full w-full flex items-center justify-center z-50">
      <div class="relative mx-auto p-6 border w-full max-w-2xl shadow-lg rounded-lg bg-gray-800 border-gray-700">
        <div class="absolute top-0 right-0 pt-4 pr-4">
          <button 
            @click="showCreateModal = false"
            class="text-gray-400 hover:text-white focus:outline-none"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <h3 class="text-xl font-medium leading-6 text-blue-300 mb-4">创建新协议</h3>
        <form @submit.prevent="handleCreateProtocol">
          <div class="mb-4">
            <label for="newProtocolPath" class="block text-sm font-medium text-gray-300 mb-1">文件路径</label>
            <input
              type="text"
              id="newProtocolPath"
              v-model="newProtocol.path"
              required
              placeholder="例如: my_protocols/protocol.py"
              class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div class="mb-4">
            <label for="newProtocolContent" class="block text-sm font-medium text-gray-300 mb-1">初始内容</label>
            <textarea
              id="newProtocolContent"
              v-model="newProtocol.content"
              rows="12"
              required
              placeholder="# Your Python MCP protocol code here
from repository.mcp_base import mcp

@mcp.protocol(...)
def my_new_protocol(...):
    ..."
              class="mt-1 block w-full p-3 bg-gray-900 border border-gray-700 rounded-md font-mono text-sm text-gray-100 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
          <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
            <button
              type="submit"
              :disabled="protocolStore.loading"
              class="w-full inline-flex justify-center items-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:col-start-2 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="protocolStore.loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              创建
            </button>
            <button
              type="button"
              @click="showCreateModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-600 shadow-sm px-4 py-2 bg-gray-700 text-base font-medium text-gray-200 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 sm:mt-0 sm:col-start-1 sm:text-sm"
            >
              取消
            </button>
          </div>
        </form>
        <p v-if="createError" class="text-red-400 text-sm mt-3 bg-red-900 bg-opacity-30 p-2 rounded border border-red-800">
          {{ createError }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useProtocolStore } from '../../store/protocols';
import type { ProtocolCreate } from '../../types/protocols';

const protocolStore = useProtocolStore();

const editableContent = ref('');
const showCreateModal = ref(false);
const newProtocol = ref<ProtocolCreate>({ path: '', content: '' });
const createError = ref<string | null>(null);
const searchQuery = ref('');

// 获取协议列表和服务信息
onMounted(() => {
  protocolStore.fetchProtocols();
  protocolStore.fetchServiceInfo();
});

// 监听选中协议的变化，更新编辑器内容
watch(() => protocolStore.selectedProtocolContent, (newContent) => {
  editableContent.value = newContent ?? '';
});

// 计算内容是否有变化
const isContentChanged = computed(() => {
  return editableContent.value !== (protocolStore.selectedProtocolContent ?? '');
});

// 过滤协议列表
const filteredProtocols = computed(() => {
  if (!searchQuery.value) return protocolStore.protocols;
  const query = searchQuery.value.toLowerCase();
  return protocolStore.protocols.filter(protocol => 
    protocol.name.toLowerCase().includes(query) || 
    protocol.path.toLowerCase().includes(query) ||
    (protocol.description && protocol.description.toLowerCase().includes(query))
  );
});

// 选择协议
function selectProtocol(protocolPath: string) {
  if (protocolStore.selectedProtocolPath !== protocolPath) {
    protocolStore.fetchProtocolContent(protocolPath);
  }
}

// 获取当前选中协议的名称
function getProtocolName() {
  const protocol = protocolStore.protocols.find(p => p.path === protocolStore.selectedProtocolPath);
  return protocol ? protocol.name : protocolStore.selectedProtocolPath;
}

// 格式化日期
function formatDate(dateString: string) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit'
  }).format(date);
}

// 保存更改
async function saveProtocolChanges() {
  if (!protocolStore.selectedProtocolPath || !isContentChanged.value) return;
  try {
    await protocolStore.updateProtocol(protocolStore.selectedProtocolPath, { content: editableContent.value });
    // 可以在这里添加成功提示，例如使用 toast
    alert('协议已成功更新！');
  } catch (err) {
    // 错误已在 store 中处理，这里可以添加 UI 反馈
    alert(`更新失败: ${protocolStore.error}`);
  }
}

// 处理创建协议
async function handleCreateProtocol() {
  createError.value = null; // 清除之前的错误
  try {
    await protocolStore.createProtocol(newProtocol.value);
    showCreateModal.value = false;
    newProtocol.value = { path: '', content: '' }; // 重置表单
    alert('协议已成功创建！');
  } catch (err) {
    createError.value = protocolStore.error ?? '创建协议时发生未知错误';
  }
}

// 确认删除
async function confirmDeleteProtocol() {
  if (!protocolStore.selectedProtocolPath) return;
  if (confirm(`确定要删除协议 ${protocolStore.selectedProtocolPath} 吗？此操作不可恢复！`)) {
    try {
      await protocolStore.deleteProtocol(protocolStore.selectedProtocolPath);
      alert('协议已成功删除！');
    } catch (err) {
      alert(`删除失败: ${protocolStore.error}`);
    }
  }
}

// MCP服务控制
async function startService() {
  try {
    const result = await protocolStore.controlService({ action: 'start' });
    if (result.success) {
      alert('MCP服务已成功启动！');
    } else {
      alert(`启动失败: ${result.message}`);
    }
  } catch (err) {
    alert(`操作失败: ${protocolStore.error}`);
  }
}

async function stopService() {
  try {
    const result = await protocolStore.controlService({ action: 'stop' });
    if (result.success) {
      alert('MCP服务已成功停止！');
    } else {
      alert(`停止失败: ${result.message}`);
    }
  } catch (err) {
    alert(`操作失败: ${protocolStore.error}`);
  }
}

async function restartService() {
  try {
    const result = await protocolStore.controlService({ action: 'restart' });
    if (result.success) {
      alert('MCP服务已成功重启！');
    } else {
      alert(`重启失败: ${result.message}`);
    }
  } catch (err) {
    alert(`操作失败: ${protocolStore.error}`);
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #2d3748;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #4a5568;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #718096;
}
</style> 