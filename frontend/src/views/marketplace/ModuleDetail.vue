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

              <!-- <div v-if="moduleTools.length > 0">
                <h3 class="text-lg font-medium mb-4">工具列表</h3>
                <el-table :data="moduleTools" border>
                  <el-table-column prop="name" label="工具名称" />
                  <el-table-column prop="description" label="描述" show-overflow-tooltip />
                  <el-table-column prop="function_name" label="函数名" width="150" />
                  <el-table-column label="状态" width="100">
                    <template #default="scope">
                      <el-tag :type="scope.row.is_enabled ? 'success' : 'danger'">
                        {{ scope.row.is_enabled ? '已启用' : '已禁用' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="150">
                    <template #default="scope">
                      <el-button type="primary" size="small" @click="switchToToolTest(scope.row)">测试</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <el-empty v-else description="没有找到工具" /> -->
            </el-tab-pane>

            <el-tab-pane label="工具测试" name=" -->tool-test">
              <div v-if="currentTool" class="tool-test-panel">
                <div class="mb-4">
                  <h3 class="text-lg font-medium mb-2">{{ currentTool.name }}</h3>
                  <p class="text-gray-600 mb-4">{{ currentTool.description }}</p>

                  <!-- 参数输入表单 -->
                  <el-form :model="testParams" label-position="top">
                    <el-form-item v-for="param in getToolParams()" :key="param.name"
                      :label="param.name + (param.required ? ' (必填)' : '')">
                      <el-input v-model="testParams[param.name]" :placeholder="param.type" />
                    </el-form-item>

                    <el-form-item>
                      <el-button type="primary" @click="testTool" :loading="testing">执行测试</el-button>
                    </el-form-item>
                  </el-form>
                </div>

                <!-- 测试结果 -->
                <div v-if="testResult" class="mt-4">
                  <h4 class="font-medium mb-2">测试结果</h4>
                  <el-alert v-if="testError" :title="testError" type="error" show-icon class="mb-3" />
                  <div v-else class="bg-gray-50 p-4 rounded">
                    <pre class="whitespace-pre-wrap">{{ formatResult(testResult) }}</pre>
                  </div>
                </div>
              </div>
              <el-empty v-else description="请选择要测试的工具" />
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
                    :indent-with-tab="true" :tab-size="4" class="code-editor" />
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
import type { McpModuleInfo, McpToolInfo, McpToolParameter } from '../../types/marketplace';
import Codemirror from 'vue-codemirror6';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import VueMarkdownRender from 'vue-markdown-render';

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
const extensions = [python(), oneDark];

// 加载模块详情
async function loadModuleInfo() {
  loading.value = true;
  try {
    moduleInfo.value = await getModule(moduleId.value);
    moduleTools.value = await getModuleTools(moduleId.value);

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
    const result = await testModuleTool(currentTool.value!.id, testParams.value);
    testResult.value = result;
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
</style>