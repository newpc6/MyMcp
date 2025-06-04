<template>
  <div class="flex">
    <!-- 左侧工具列表 -->
    <div class="mcp-tool-list border-r">
      <div class="mb-4">
        <el-input v-model="searchQuery" placeholder="搜索工具名称" prefix-icon="Search" clearable />
      </div>

      <div class="tools-list">
        <div v-for="tool in filteredTools" :key="tool.function_name" class="tool-card mb-3 cursor-pointer"
          :class="{ 'tool-card-active': currentTool && currentTool.function_name === tool.function_name }"
          @click="selectTool(tool)">
          <el-text truncated>
            <h3 class="text-lg font-bold mb-1">{{ tool.name }}</h3>
          </el-text>
          <el-text truncated>{{ tool.description }}</el-text>
        </div>

        <el-empty v-if="filteredTools.length === 0" description="没有找到工具" />
      </div>
    </div>

    <!-- 右侧工具详情和测试区域 -->
    <div class="tool-test-content">
      <div v-if="currentTool" class="tool-test-area">
        <div class="mb-6">
          <h2 class="text-xl font-bold mb-2 text-primary">{{ currentTool.name }}</h2>
          <p class="text-gray-600 mb-4 whitespace-pre-line">{{ currentTool.description }}</p>

          <!-- 参数输入表单 -->
          <el-card shadow="hover" class="mb-4 tool-params-card">
            <template #header>
              <div class="flex justify-between items-center">
                <span class="font-medium">参数设置</span>
              </div>
            </template>

            <el-form :model="testParams" label-position="top">
              <el-form-item v-for="param in getToolParams()" :key="param.name"
                :label="param.name + (param.required ? ' (必填)' : '')"
                :class="{ 'required-param': param.required }">
                <div class="text-sm text-gray-500 mb-1">{{ param.type }}</div>
                <el-input 
                  v-model="testParams[param.name]" 
                  :placeholder="'请输入' + param.name"
                  :class="{ 'required-input': param.required && (!testParams[param.name] || String(testParams[param.name]).trim() === '') }"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="testTool" :loading="testing" :disabled="!canExecuteTest" class="w-full test-button">
                  执行测试
                </el-button>
                
                <!-- 必填参数提示 -->
                <div v-if="!canExecuteTest && hasRequiredParams" class="mt-2">
                  <el-alert 
                    type="warning" 
                    :closable="false" 
                    show-icon
                    size="small"
                    class="required-params-alert"
                  >
                    <template #title>
                      <span class="text-sm">请填写所有必填参数后再执行测试</span>
                    </template>
                  </el-alert>
                </div>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 测试结果 -->
          <el-card v-if="testResult !== null || testError" shadow="hover" class="result-card">
            <template #header>
              <div class="flex justify-between items-center">
                <span class="font-medium">测试结果</span>
                <el-tag v-if="testResult !== null && !testError" type="success" size="small">成功</el-tag>
                <el-tag v-else-if="testError" type="danger" size="small">失败</el-tag>
              </div>
            </template>

            <el-alert v-if="testError" :title="testError" type="error" show-icon class="mb-3" />
            <div v-else-if="testResult !== null" class="result-content-wrapper">
              <pre class="whitespace-pre-wrap result-content">{{ formatResult(testResult) }}</pre>
            </div>
            <div v-else class="result-content-wrapper">
              <el-text type="info">暂无测试结果</el-text>
            </div>
          </el-card>
        </div>
      </div>

      <el-empty v-else description="请选择要测试的工具" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Search } from '@element-plus/icons-vue';
import type { McpToolInfo, McpToolParameter } from '../../../types/marketplace';

const props = defineProps<{
  tools: McpToolInfo[];
  moduleId: number;
}>();

const emit = defineEmits<{
  (e: 'test', toolName: string, params: Record<string, any>, callback: (result: any, error?: any) => void): void;
}>();

const searchQuery = ref('');
const currentTool = ref<McpToolInfo | null>(null);
const testParams = ref<Record<string, any>>({});
const testResult = ref<any>(null);
const testError = ref<string | null>(null);
const testing = ref(false);

// 过滤工具列表
const filteredTools = computed(() => {
  if (!searchQuery.value) return props.tools;

  const query = searchQuery.value.toLowerCase();
  return props.tools.filter(tool =>
    tool.name.toLowerCase().includes(query) ||
    tool.description.toLowerCase().includes(query)
  );
});

// 检查是否所有必填参数都已填写
const canExecuteTest = computed(() => {
  if (!currentTool.value) return false;
  
  const requiredParams = getToolParams().filter(param => param.required);
  if (requiredParams.length === 0) return true; // 没有必填参数时可以执行
  
  return requiredParams.every(param => {
    const value = testParams.value[param.name];
    return value !== undefined && value !== null && String(value).trim() !== '';
  });
});

// 检查是否有必填参数
const hasRequiredParams = computed(() => {
  return getToolParams().some(param => param.required);
});

// 选择工具
function selectTool(tool: McpToolInfo) {
  currentTool.value = tool;
  testParams.value = {};
  testResult.value = null;
  testError.value = null;
}

// 获取工具参数列表
function getToolParams(): McpToolParameter[] {
  if (!currentTool.value?.parameters) return [];
  return currentTool.value.parameters;
}

// 测试工具
async function testTool() {
  if (!currentTool.value) return;

  testResult.value = null;
  testError.value = null;
  testing.value = true;

  try {
    const toolName = currentTool.value.function_name;

    // 构建调用参数对象
    const params: Record<string, any> = {};
    for (const param of getToolParams()) {
      // 如果有参数值，则添加到请求中
      if (testParams.value[param.name] !== undefined && testParams.value[param.name] !== '') {
        // 尝试将字符串转换为适当的类型
        let value = testParams.value[param.name];
        try {
          // 如果参数是数组类型且提供的是字符串，尝试解析成数组
          if ((param.type.includes('List') || param.type.includes('list')) && typeof value === 'string') {
            // 尝试解析为JSON数组
            if (value.trim().startsWith('[') && value.trim().endsWith(']')) {
              value = JSON.parse(value);
            }
            // 否则按逗号分隔处理
            else {
              value = value.split(',').map(item => {
                const trimmed = item.trim();
                // 尝试将数字字符串转换为数字
                if (!isNaN(Number(trimmed))) {
                  return Number(trimmed);
                }
                return trimmed;
              });
            }
          }
          // 如果参数是数字类型且提供的是字符串，尝试解析成数字
          else if ((param.type.includes('int') || param.type.includes('float')) && typeof value === 'string') {
            value = Number(value);
          }
          // 如果参数是字典类型且提供的是字符串，尝试解析成对象
          else if ((param.type.includes('Dict') || param.type.includes('dict')) && typeof value === 'string') {
            if (value.trim().startsWith('{') && value.trim().endsWith('}')) {
              value = JSON.parse(value);
            }
          }
        } catch (e) {
          console.warn(`无法解析参数 ${param.name} 的值`, e);
          // 如果解析失败，使用原始值
        }

        params[param.name] = value;
      }
    }

    console.log('发送测试请求:', { toolName, params });
    
    const callback = (result: any, error?: any) => {
      if (error) {
        console.error("工具测试失败", error);
        testError.value = error.response?.data?.detail || error.message || '执行失败';
      } else {
        console.log('接收到测试结果:', result);
        testResult.value = result;
        console.log('测试结果已设置:', testResult.value);
      }
      testing.value = false;
    };
    
    emit('test', toolName, params, callback);
  } catch (error: any) {
    console.error("工具测试失败", error);
    testError.value = error.response?.data?.detail || error.message || '执行失败';
    testing.value = false;
  }
}

// 格式化结果显示
function formatResult(result: any) {
  if (result === null || result === undefined) {
    return '无结果';
  }
  
  if (typeof result === 'object') {
    // 如果是标准的接口响应格式 {code, message, data}
    if (result.hasOwnProperty('code') && result.hasOwnProperty('message')) {
      const formatted = {
        状态码: result.code,
        消息: result.message,
        数据: result.data || '无数据'
      };
      return JSON.stringify(formatted, null, 2);
    }
    return JSON.stringify(result, null, 2);
  }
  
  return String(result);
}

// 如果有tools数据并且没有选中工具，默认选择第一个
if (props.tools.length > 0 && !currentTool.value) {
  selectTool(props.tools[0]);
}
</script>

<script lang="ts">
export default {
  name: 'ToolTestPanel'
}
</script>

<style scoped>
.mcp-tool-list {
  width: 400px;
  padding-right: 20px;
}

.tool-test-content {
  flex: 1;
  padding-left: 24px;
}

.tool-card {
  padding: 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #ebeef5;
  overflow: hidden;
  position: relative;
}

.tool-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(240, 249, 255, 0.9));
}

.tool-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #409eff, #79bbff);
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 2px;
}

.tool-card:hover::before,
.tool-card-active::before {
  opacity: 1;
}

.tool-card-active {
  background: linear-gradient(135deg, rgba(240, 249, 255, 0.9), rgba(230, 247, 255, 0.9));
  border-color: #b3d8ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.tool-params-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: linear-gradient(135deg, #fff, #f9fdff);
}

.result-card {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 16px;
  backdrop-filter: blur(5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.result-content {
  max-height: 300px;
  overflow-y: auto;
}

.result-content-wrapper {
  background-color: rgba(246, 248, 250, 0.8);
  border-radius: 12px;
  padding: 12px;
}

.tools-list {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
  scrollbar-width: thin;
}

.tools-list::-webkit-scrollbar {
  width: 6px;
}

.tools-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 3px;
}

.tools-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.tools-list::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.2);
}

.tool-test-area {
  padding: 8px;
}

:deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-button.test-button) {
  border-radius: 12px;
  background: linear-gradient(90deg, #409eff, #79bbff);
  border: none;
  height: 40px;
  font-weight: 500;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

:deep(.el-button.test-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
  background: linear-gradient(90deg, #409eff, #a0cfff);
}

:deep(.el-button.test-button.is-disabled) {
  background: linear-gradient(90deg, #c0c4cc, #d3d4d6) !important;
  box-shadow: none !important;
  transform: none !important;
  cursor: not-allowed !important;
}

.required-params-alert {
  border-radius: 8px;
  border: 1px solid #f0ad4e;
  background: rgba(255, 193, 7, 0.1);
}

.required-params-alert :deep(.el-alert__icon) {
  color: #f0ad4e;
}

.required-params-alert :deep(.el-alert__title) {
  color: #856404;
  font-weight: 500;
}

.required-param :deep(.el-form-item__label) {
  position: relative;
}

.required-param :deep(.el-form-item__label::before) {
  content: "*";
  color: #f56c6c;
  margin-right: 4px;
  font-weight: bold;
}

.required-input :deep(.el-input__wrapper) {
  border: 2px solid #f56c6c !important;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2) !important;
}

.required-input :deep(.el-input__wrapper:hover) {
  border-color: #f56c6c !important;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.3) !important;
}

:deep(.el-input__inner) {
  border-radius: 10px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>