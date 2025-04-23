<template>
  <el-container class="p-4">
    <el-main class="p-0">
      <div v-if="loading" class="py-10">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else>
        <!-- 顶部信息卡片 -->
        <el-card class="mb-4" shadow="never">
          <div class="flex items-start">
            <el-avatar :icon="getModuleIcon(moduleInfo)" :size="64" class="mr-6"></el-avatar>
            <div class="flex-1">
              <div class="flex justify-between">
                <h2 class="text-xl font-bold mb-2">{{ moduleInfo.name }}</h2>
                <el-button @click="goBack">返回列表</el-button>
              </div>

              <p class="text-gray-600 mb-4">{{ moduleInfo.description }}</p>

              <div class="flex flex-wrap gap-2 mb-3">
                <el-tag v-for="tag in moduleInfo.tags" :key="tag" size="small" class="mr-1">{{ tag }}</el-tag>
                <el-tag size="small" :type="moduleInfo.is_hosted ? 'success' : 'primary'">
                  {{ moduleInfo.is_hosted ? '托管' : '本地' }}
                </el-tag>
                <el-tag size="small" type="info">
                  {{ moduleInfo.tools_count }} 个工具
                </el-tag>
              </div>

              <div class="text-sm text-gray-500">
                <div><strong>模块路径:</strong> {{ moduleInfo.module_path }}</div>
                <div v-if="moduleInfo.author"><strong>作者:</strong> {{ moduleInfo.author }}</div>
                <div v-if="moduleInfo.version"><strong>版本:</strong> {{ moduleInfo.version }}</div>
                <div><strong>创建时间:</strong> {{ moduleInfo.created_at }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 标签页 -->
        <el-card shadow="never">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="服务详情" name="service-details">
              <!-- 工具列表 -->
              <div v-if="moduleInfo.markdown_docs" class="markdown-content mb-6">
                <VueMarkdownRender :source="moduleInfo.markdown_docs" class="markdown-body" />
              </div>

              <el-empty v-else description="没有找到工具" />
            </el-tab-pane>

            <el-tab-pane label="工具测试" name="tool-test">
              <div class="flex">
                <!-- 左侧工具列表 -->
                <div class="mcp-tool-list border-r">
                  <div class="mb-4">
                    <el-input v-model="toolSearchQuery" placeholder="搜索工具名称" prefix-icon="Search" clearable />
                  </div>

                  <div class="tools-list max-h-[600px] overflow-y-auto pr-2">
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
                            :label="param.name + (param.required ? ' (必填)' : '')">
                            <div class="text-xs text-gray-500 mb-1">{{ param.type }}</div>
                            <el-input v-model="testParams[param.name]" :placeholder="'请输入' + param.name" />
                          </el-form-item>

                          <el-form-item>
                            <el-button type="primary" @click="testTool" :loading="testing" class="w-full test-button">
                              执行测试
                            </el-button>
                          </el-form-item>
                        </el-form>
                      </el-card>

                      <!-- 测试结果 -->
                      <el-card v-if="testResult || testError" shadow="hover" class="result-card">
                        <template #header>
                          <div class="flex justify-between items-center">
                            <span class="font-medium">测试结果</span>
                          </div>
                        </template>

                        <el-alert v-if="testError" :title="testError" type="error" show-icon class="mb-3" />
                        <div v-else class="result-content-wrapper">
                          <pre class="whitespace-pre-wrap result-content">{{ formatResult(testResult) }}</pre>
                        </div>
                      </el-card>
                    </div>
                  </div>

                  <el-empty v-else description="请选择要测试的工具" />
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="代码查看/编辑" name="code-edit">
              <div class="code-editor-container">
                <div v-if="!moduleInfo.code" class="p-4">
                  <el-empty description="该模块暂无代码" />
                </div>
                <div v-else>
                  <div class="mb-4 flex justify-between items-center">
                    <h3 class="text-lg font-medium">模块代码</h3>
                    <div>
                      <el-button type="primary" size="small" @click="saveModuleCode" :loading="saving"
                        :disabled="!hasCodeChanged">
                        保存修改
                      </el-button>
                    </div>
                  </div>
                  <Codemirror v-model="codeContent" :extensions="extensions" :style="{ height: '500px' }"
                    :indent-with-tab="true" :tab-size="4" class="code-editor" @ready="handleEditorCreated" />
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElNotification } from 'element-plus';
import {
  getModule, getModuleTools, testModuleTool, updateModule
} from '../../api/marketplace';
import httpClient from '../../utils/http-client';
import type { McpModuleInfo, McpToolInfo, McpToolParameter } from '../../types/marketplace';
import Codemirror from 'vue-codemirror6';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import VueMarkdownRender from 'vue-markdown-render';
import { keymap } from '@codemirror/view';
import { defaultKeymap } from '@codemirror/commands';

const route = useRoute();
const router = useRouter();
const moduleId = computed(() => Number(route.params.id));

const loading = ref(true);
const moduleInfo = ref<McpModuleInfo>({} as McpModuleInfo);
const moduleTools = ref<McpToolInfo[]>([]);
const activeTab = ref('service-details');
const currentTool = ref<McpToolInfo | null>(null);
const testParams = ref<Record<string, any>>({});
const testResult = ref<any>(null);
const testError = ref<string | null>(null);
const testing = ref(false);
const codeContent = ref('');
const originalCode = ref('');
const saving = ref(false);
const hasCodeChanged = computed(() => {
  return codeContent.value !== originalCode.value;
});

// CodeMirror 扩展配置
const extensions = [
  python(), 
  oneDark,
  keymap.of(defaultKeymap),
];

// 添加常量和方法
const toolSearchQuery = ref('');

// 过滤工具列表
const filteredTools = computed(() => {
  if (!toolSearchQuery.value) return moduleTools.value;

  const query = toolSearchQuery.value.toLowerCase();
  return moduleTools.value.filter(tool =>
    tool.name.toLowerCase().includes(query) ||
    tool.description.toLowerCase().includes(query)
  );
});

// 选择工具
function selectTool(tool: McpToolInfo) {
  currentTool.value = tool;
  testParams.value = {};
  testResult.value = null;
  testError.value = null;
}

// 加载模块详情
async function loadModuleInfo() {
  loading.value = true;
  try {
    moduleInfo.value = await getModule(moduleId.value);
    moduleTools.value = await getModuleTools(moduleId.value);

    // 默认选中第一个工具
    if (moduleTools.value.length > 0) {
      selectTool(moduleTools.value[0]);
    }

    // 如果模块有代码，初始化编辑器内容
    if (moduleInfo.value.code) {
      codeContent.value = moduleInfo.value.code;
      originalCode.value = moduleInfo.value.code;
    }
  } catch (error) {
    console.error("加载模块详情失败", error);
    ElNotification({
      title: '错误',
      message: '加载模块详情失败',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
}

// 获取工具参数列表
function getToolParams(): McpToolParameter[] {
  if (!currentTool.value?.parameters) return [];
  return currentTool.value.parameters;
}

// 测试工具
async function testTool() {
  testResult.value = null;
  testError.value = null;
  testing.value = true;

  try {
    // 由于新的工具没有ID，我们需要使用模块ID和函数名来调用
    const toolName = currentTool.value!.function_name;
    const moduleId = moduleInfo.value.id;

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

    // 直接使用现有API，通过endpoint修改为调用新的API
    const response = await httpClient.post(
      `/api/execute/module/${moduleId}/function/${toolName}`,
      params
    );
    testResult.value = response.data.result;
  } catch (error: any) {
    console.error("工具测试失败", error);
    testError.value = error.response?.data?.detail || error.message || '执行失败';
  } finally {
    testing.value = false;
  }
}

// 格式化结果显示
function formatResult(result: any) {
  if (typeof result === 'object') {
    return JSON.stringify(result, null, 2);
  }
  return result;
}

// 格式化类型信息
function formatType(type: string): string {
  if (!type) return 'unknown';

  // 简化类型信息，移除<class>前缀
  if (type.startsWith('<class ')) {
    return type.replace(/<class '(.+?)'>/, '$1');
  }

  // 简化typing类型
  if (type.startsWith('typing.')) {
    return type.replace('typing.', '');
  }

  return type;
}

// 切换到工具测试页
function switchToToolTest(tool: McpToolInfo) {
  currentTool.value = tool;
  testParams.value = {};
  testResult.value = null;
  testError.value = null;
  activeTab.value = 'tool-test';
}

// 返回列表页
function goBack() {
  router.push('/marketplace');
}

// 根据模块类型获取图标
function getModuleIcon(module: McpModuleInfo) {
  // 根据模块类型或名称返回不同的图标
  if (!module?.name) return 'Tools';

  if (module.name.toLowerCase().includes('tavily')) {
    return 'Search';
  } else if (module.name.toLowerCase().includes('fetch')) {
    return 'Link';
  } else if (module.name.toLowerCase().includes('github')) {
    return 'Platform';
  } else {
    return 'Tools';
  }
}

// 保存模块代码
async function saveModuleCode() {
  if (!hasCodeChanged.value) return;

  saving.value = true;
  try {
    await updateModule(moduleId.value, { code: codeContent.value });
    originalCode.value = codeContent.value;
    ElNotification({
      title: '成功',
      message: '模块代码已保存',
      type: 'success'
    });
  } catch (error) {
    console.error("保存模块代码失败", error);
    ElNotification({
      title: '错误',
      message: '保存模块代码失败',
      type: 'error'
    });
  } finally {
    saving.value = false;
  }
}

// 在代码编辑页面中添加编辑器扩展配置
function handleEditorCreated(editor: any) {
  // 这里可以添加编辑器创建后的回调处理
  console.log('编辑器已创建');
}

// 页面加载时获取模块详情
onMounted(() => {
  loadModuleInfo();
});
</script>

<style scoped>
.tool-test-panel {
  max-width: 800px;
}

.code-editor {
  border: 1px solid #eee;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
}

:deep(.cm-editor) {
  height: 100%;
}

:deep(.cm-scroller) {
  overflow: auto;
}

.code-editor-container {
  width: 100%;
}

.markdown-content {
  padding: 1rem;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #eee;
}

.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  font-weight: 600;
}

.markdown-body h1 {
  font-size: 2em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.markdown-body h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

.markdown-body h3 {
  font-size: 1.25em;
}

.markdown-body h4 {
  font-size: 1em;
}

.markdown-body p {
  margin-bottom: 1em;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 2em;
  margin-bottom: 1em;
}

.markdown-body li {
  margin-bottom: 0.5em;
}

.markdown-body code {
  font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.markdown-body pre {
  background-color: #f6f8fa;
  border-radius: 3px;
  padding: 1em;
  overflow: auto;
  margin-bottom: 1em;
}

.markdown-body pre code {
  background-color: transparent;
  padding: 0;
}

.markdown-body blockquote {
  border-left: 0.25em solid #dfe2e5;
  padding: 0 1em;
  color: #6a737d;
  margin-bottom: 1em;
}

.markdown-body img {
  max-width: 100%;
  height: auto;
}

.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}

.markdown-body table th,
.markdown-body table td {
  border: 1px solid #dfe2e5;
  padding: 6px 13px;
}

.markdown-body table th {
  background-color: #f6f8fa;
  font-weight: 600;
}

.markdown-body hr {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: #e1e4e8;
  border: 0;
}

.tool-card {
  padding: 12px;
  border-radius: 8px;
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

.result-card {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 12px;
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
  border-radius: 8px;
  padding: 12px;
}

.mcp-tool-list {
  width: 400px;
  padding-right: 20px;
}

.tool-test-content {
  flex: 1;
  padding-left: 24px;
}

.tool-params-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: linear-gradient(135deg, #fff, #f9fdff);
}

.tool-test-area {
  padding: 8px;
}

:deep(.el-card) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-button.test-button) {
  border-radius: 8px;
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

:deep(.el-input__inner) {
  border-radius: 8px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>