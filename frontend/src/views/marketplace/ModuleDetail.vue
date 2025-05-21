<template>
  <el-container class="p-4">
    <el-main class="p-0">
      <div v-if="loading" class="py-10">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else>
        <!-- 顶部信息区域 - 使用flex布局水平排列两个卡片 -->
        <div class="flex gap-4 mb-4">
          <!-- 模块信息卡片 -->
          <el-card class="module-info-card" style="width: 55%" shadow="never">
            <div class="flex items-start">
              <el-avatar :icon="getModuleIcon(moduleInfo)" :size="64" class="mr-6"></el-avatar>
              <div class="flex-1">
                <div class="flex justify-between">
                  <h2 class="text-xl font-bold mb-2">{{ moduleInfo.name }}</h2>
                  <div>
                    <el-button type="primary" @click="showEditDialog" class="mr-2"
                      v-if="hasEditPermission">编辑</el-button>
                    <el-button type="danger" @click="handleDeleteModule" class="mr-2"
                      v-if="hasEditPermission">删除</el-button>
                    <el-button @click="goBack" class="return-btn">返回广场</el-button>
                  </div>
                </div>

                <div class="flex justify-between">
                  <div class="flex-1 mr-6">
                    <p class="text-gray-600 mb-4">{{ moduleInfo.description }}</p>

                    <div class="flex flex-wrap mb-3">
                      <el-tag v-for="tag in moduleInfo.tags" :key="tag" size="small" class="mr-1 tag-item">{{ tag
                        }}</el-tag>
                      <el-tag size="small" :type="moduleInfo.is_hosted ? 'success' : 'primary'" class="tag-item">
                        {{ moduleInfo.is_hosted ? '托管' : '本地' }}
                      </el-tag>
                      <el-tag size="small" type="info" class="tag-item">
                        {{ moduleInfo.tools_count }} 个工具
                      </el-tag>
                    </div>
                  </div>

                  <div class="module-info-meta">
                    <div v-if="moduleInfo.author" class="module-meta-item"><strong>作者:</strong> {{ moduleInfo.author }}
                    </div>
                    <div v-if="moduleInfo.version" class="module-meta-item"><strong>版本:</strong> {{ moduleInfo.version
                      }}</div>
                    <div v-if="moduleInfo.creator_name" class="module-meta-item"><strong>创建者:</strong> {{
                      moduleInfo.creator_name }}</div>
                    <div class="module-meta-item">
                      <strong>状态:</strong>
                      <el-tag size="small" :type="moduleInfo.is_public ? 'success' : 'danger'" class="ml-1">
                        {{ moduleInfo.is_public ? '公开' : '私有' }}
                      </el-tag>
                    </div>
                    <div class="module-meta-item"><strong>创建时间:</strong> {{ moduleInfo.created_at }}</div>
                    <div class="module-meta-item"><strong>更新时间:</strong> {{ moduleInfo.updated_at }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 服务发布卡片 -->
          <el-card shadow="never" class="service-card" style="width: 45%;">
            <template #header>
              <div class="card-header">
                <h3 class="text-lg font-bold">服务发布</h3>
                <div class="service-actions" v-if="!loadingServices">
                  <el-button type="primary" size="small" @click="handlePublishService()">
                    发布服务
                  </el-button>
                </div>
              </div>
            </template>

            <div v-if="loadingServices" class="text-center py-2">
              <el-skeleton :rows="1" animated />
            </div>
            <div v-else-if="services.length === 0" class="text-center py-4">
              <el-empty description="暂无服务" :image-size="60">
                <template #description>
                  <p class="text-gray-500">还没有发布服务，点击上方按钮发布</p>
                </template>
              </el-empty>
            </div>
            <div v-else>
              <el-table :data="services" style="width: 100%" size="small" class="service-table"
                :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266', fontWeight: 'bold' }">
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="scope">
                    <el-tag :type="getStatusType(scope.row.status)" size="small">
                      {{ getStatusText(scope.row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="服务名称" min-width="120"></el-table-column>
                <el-table-column prop="sse_url" label="SSE URL" min-width="220">
                  <template #default="scope">
                    <div class="flex items-center">
                      <el-tooltip :content="scope.row.sse_url" placement="top" :show-after="500">
                        <el-input v-model="scope.row.sse_url" readonly size="small" class="flex-1 mr-1"
                          :title="scope.row.sse_url" disabled />
                      </el-tooltip>
                      <el-button type="primary" circle size="small" @click="copyUrl(scope.row.sse_url)" title="复制URL">
                        <el-icon>
                          <DocumentCopy />
                        </el-icon>
                      </el-button>
                      <el-button type="success" circle size="small" @click="copyAsEgovakbUrl(scope.row.sse_url)"
                        title="复制为egovakb格式">
                        <el-icon>
                          <Connection />
                        </el-icon>
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="140" />
                <el-table-column fixed="right" label="操作" width="200">
                  <template #default="scope">
                    <el-button v-if="scope.row.status === 'running'" type="info" size="small"
                      @click="handleStopService(scope.row.service_uuid)">
                      停止
                    </el-button>
                    <el-button v-else-if="scope.row.status === 'stopped'" type="success" size="small"
                      @click="handleStartService(scope.row.service_uuid)">
                      启动
                    </el-button>
                    <el-button v-else-if="scope.row.status === 'error'" type="warning" size="small"
                      @click="handleStartService(scope.row.service_uuid)">
                      重启
                    </el-button>
                    <el-button type="primary" size="small" @click="viewServiceParams(scope.row)" title="查看参数">
                      参数
                    </el-button>
                    <el-button type="danger" size="small" @click="handleUninstallService(services[0].service_uuid)">
                      卸载
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>

        <!-- 标签页 -->
        <el-card shadow="never" class="tabs-card">
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
                            :label="param.name + (param.required ? ' (必填)' : '')">
                            <div class="text-sm text-gray-500 mb-1">{{ param.type }}</div>
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
                  <div class="code-editor-header">
                    <h3 class="editor-title">模块代码</h3>
                    <div class="editor-actions">
                      <el-alert v-if="!hasEditPermission" type="warning" :closable="false" show-icon
                        title="您只能查看代码，没有编辑权限" class="mr-4" />
                      <el-button type="primary" size="small" @click="formatPythonCode" :loading="saving"
                        v-if="hasEditPermission">
                        格式化代码
                      </el-button>
                      <el-button type="primary" size="small" @click="saveModuleCode" :loading="saving"
                        :disabled="!hasCodeChanged" v-if="hasEditPermission">
                        保存修改
                      </el-button>
                    </div>
                  </div>
                  <div class="code-editor-wrapper">
                    <Codemirror v-model="codeContent" :extensions="extensions" class="code-editor"
                      :indent-with-tab="true" :tab-size="4" @ready="handleEditorCreated"
                      style="overflow: auto; height: 100%;" :readonly="!hasEditPermission" basic />
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </el-main>

    <!-- 编辑模块对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑MCP服务" width="60%" :destroy-on-close="true">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px" label-position="top">
        <el-form-item label="服务名称" prop="name">
          <el-input v-model.trim="editForm.name" placeholder="请输入服务名称" clearable></el-input>
        </el-form-item>

        <el-form-item label="服务描述" prop="description">
          <textarea v-model="editForm.description" rows="3" placeholder="请输入服务描述" class="el-textarea__inner"
            style="width: 100%; border-radius: 4px; border: 1px solid #DCDFE6; padding: 10px;" clearable></textarea>
        </el-form-item>

        <el-form-item label="版本" prop="version">
          <el-input v-model.trim="editForm.version" placeholder="请输入版本号，例如：1.0.0" clearable></el-input>
        </el-form-item>

        <el-form-item label="标签" prop="tags">
          <el-select v-model="editForm.tags" multiple filterable allow-create default-first-option placeholder="请输入标签"
            style="width: 100%" clearable>
          </el-select>
        </el-form-item>

        <el-form-item label="分类" prop="category_id">
          <el-select v-model="editForm.category_id" placeholder="请选择分类" style="width: 100%" clearable>
            <el-option v-for="category in categories" :key="category.id" :label="category.name"
              :value="category.id"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="服务详情">
          <textarea v-model="editForm.markdown_docs" rows="5" placeholder="请输入服务详情" class="el-textarea__inner"
            style="width: 100%; border-radius: 4px; border: 1px solid #DCDFE6; padding: 10px; font-family: monospace;"
            clearable></textarea>
        </el-form-item>

        <el-form-item label="代码" prop="code">
          <textarea v-model="editForm.code" rows="8" placeholder="请输入Python代码" class="el-textarea__inner"
            style="width: 100%; border-radius: 4px; border: 1px solid #DCDFE6; padding: 10px; font-family: monospace;"
            clearable></textarea>
        </el-form-item>

        <!-- 配置参数编辑区域 -->
        <el-form-item label="配置参数">
          <div class="config-params-container">
            <div class="mb-4">
              <el-button type="primary" size="default" @click="addConfigParam" :icon="Plus">新增参数</el-button>
            </div>

            <div v-if="!configParams.length" class="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
              <el-empty description="暂无配置参数，点击上方按钮添加"></el-empty>
            </div>

            <el-table v-else :data="configParams" style="width: 100%" border>
              <el-table-column type="index" label="#" width="60" align="center" />

              <el-table-column label="基本信息" width="280">
                <template #default="scope">
                  <div class="param-base-info">
                    <el-form-item label="参数名称" class="mb-2">
                      <el-input v-model="scope.row.key" placeholder="参数键名，如 api_key" size="default" />
                    </el-form-item>

                    <el-form-item label="参数类型" class="mb-2">
                      <el-select v-model="scope.row.type" style="width: 100%" size="default">
                        <el-option label="文本" value="string" />
                        <el-option label="密码" value="password" />
                        <el-option label="数字" value="integer" />
                        <el-option label="布尔值" value="boolean" />
                      </el-select>
                    </el-form-item>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="显示信息" width="380">
                <template #default="scope">
                  <div class="param-display-info">
                    <el-form-item label="标题" class="mb-2">
                      <el-input v-model="scope.row.title" placeholder="参数显示名称，如 API密钥" size="default" />
                    </el-form-item>

                    <el-form-item label="描述" class="mb-2">
                      <el-input v-model="scope.row.description" placeholder="参数描述，如 您的API访问密钥" size="default" />
                    </el-form-item>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="其他设置">
                <template #default="scope">
                  <div class="flex items-center">
                    <el-form-item label="是否必填" class="mb-2 mr-4">
                      <el-switch v-model="scope.row.required" />
                    </el-form-item>

                    <el-form-item v-if="scope.row.type === 'string' || scope.row.type === 'password'" label="占位符"
                      class="mb-2">
                      <el-input v-model="scope.row.placeholder" placeholder="占位提示" size="default"
                        style="width: 160px" />
                    </el-form-item>

                    <el-form-item v-if="scope.row.type === 'integer'" label="默认值" class="mb-2">
                      <el-input-number v-model="scope.row.default" :min="0" style="width: 160px" size="default" />
                    </el-form-item>

                    <el-form-item v-if="scope.row.type === 'boolean'" label="默认值" class="mb-2">
                      <el-switch v-model="scope.row.default" />
                    </el-form-item>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="80" align="center">
                <template #default="scope">
                  <el-button type="danger" size="small" circle @click="removeConfigParam(scope.$index)" title="删除参数">
                    <el-icon>
                      <Delete />
                    </el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-form-item>

        <el-form-item label="访问权限">
          <el-radio-group v-model="editForm.is_public">
            <el-radio :label="true">公开</el-radio>
            <el-radio :label="false">私有</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditForm" :loading="updating">更新</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 发布服务对话框 -->
    <el-dialog v-model="publishDialogVisible" title="配置并发布服务" width="50%" :destroy-on-close="true">
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px" label-position="top">
        <el-form-item label="服务名称" prop="service_name" :rules="[{ required: true, message: '请输入服务名称', trigger: 'blur' }]">
          <el-input v-model="configForm.service_name" placeholder="请输入服务名称"></el-input>
        </el-form-item>

        <div v-if="!hasConfigSchema">
          <el-alert type="info" :closable="false" show-icon title="此模块没有需要配置的参数，可以直接发布。" class="mb-4" />
        </div>

        <template v-else>
          <el-alert type="warning" :closable="false" show-icon title="此模块需要配置以下参数才能发布" class="mb-4" />

          <el-divider content-position="left">配置参数</el-divider>

          <div v-for="(schema, key) in moduleInfo.config_schema" :key="key" class="mb-4">
            <el-form-item :label="schema.title || key" :prop="key" label-position="left"
              :rules="[{ required: schema.required, message: `请输入${schema.title || key}`, trigger: 'blur' }]">

              <!-- <div class="text-sm text-gray-500 mb-1">{{ schema.description }}</div> -->
              <div v-if="schema.type === 'integer'">
                <el-input-number v-model="configForm[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`" />
              </div>
              <div v-else>
                <el-input v-if="schema.type === 'password'" v-model="configForm[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`"
                  :type="schema.type === 'password' ? 'password' : 'text'" show-password />
                <el-input v-else v-model="configForm[key]"
                  :placeholder="schema.placeholder || `请输入${schema.title || key}`" />
              </div>
            </el-form-item>
          </div>
        </template>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="publishDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitConfigForm" :loading="publishing">发布服务</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 服务参数查看/编辑对话框 -->
    <el-dialog v-model="serviceParamsDialogVisible" title="服务参数设置" width="50%" :destroy-on-close="true">
      <div v-if="currentService">
        <div v-if="!currentService.config_params || Object.keys(currentService.config_params).length === 0"
          class="text-center py-4">
          <el-empty description="此服务没有配置参数" :image-size="60" />
        </div>
        <div v-else>
          <el-form ref="serviceParamsFormRef" :model="serviceParamsForm" label-width="120px" label-position="top">
            <div v-for="(value, key) in currentService.config_params" :key="key" class="mb-4">
              <el-form-item :label="getParamDisplay(key)" label-position="left">
                <div v-if="isNumeric(value)">
                  <el-input-number v-model="serviceParamsForm[key]" />
                </div>
                <div v-else-if="isBoolean(value)">
                  <el-switch v-model="serviceParamsForm[key]" />
                </div>
                <div v-else>
                  <el-input v-if="isPassword(key)" v-model="serviceParamsForm[key]" type="password" show-password />
                  <el-input v-else v-model="serviceParamsForm[key]" />
                </div>
              </el-form-item>
            </div>
          </el-form>
        </div>
      </div>
      <div v-else class="text-center py-4">
        <el-empty description="无法加载服务参数" :image-size="60" />
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="serviceParamsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateServiceParamsFunc" :loading="updatingParams">更新参数</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElNotification, ElMessage, ElMessageBox } from 'element-plus';
import {
  getModule, getModuleTools, testModuleTool, updateModule,
  listServices, publishModule, stopService, startService, uninstallService,
  testModuleFunction,
  listCategories,
  deleteModule,
  getService
} from '../../api/marketplace';
import { updateServiceParams } from '../../api/mcpServer';
import api from '../../api/index';
import type { McpModuleInfo, McpToolInfo, McpToolParameter, McpServiceInfo, McpCategoryInfo } from '../../types/marketplace';
import Codemirror from 'vue-codemirror6';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import VueMarkdownRender from 'vue-markdown-render';
import { keymap } from '@codemirror/view';
import { defaultKeymap } from '@codemirror/commands';
import { lintGutter, linter } from '@codemirror/lint';
import { indentUnit } from '@codemirror/language';
import { indentWithTab } from '@codemirror/commands';
import { EditorView } from '@codemirror/view';
import { basicSetup } from 'codemirror';
import { lineNumbers, highlightActiveLineGutter } from '@codemirror/view';
import { searchKeymap, search } from '@codemirror/search';
import { history, historyKeymap } from '@codemirror/commands';
import { bracketMatching, indentOnInput, foldGutter } from '@codemirror/language';
import { Document, DocumentCopy, Search, Delete, Plus, Connection } from '@element-plus/icons-vue';
import { fallbackCopyTextToClipboard, copyTextToClipboard } from '../../utils/copy';

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
  // 使用基础设置，提供基本编辑功能
  basicSetup,
  // 添加Python语言支持
  python(),
  // 使用暗色主题
  oneDark,
  // 添加基本键盘映射
  keymap.of(defaultKeymap),
  // 支持Tab键缩进
  keymap.of([indentWithTab]),
  // 设置缩进单位为4个空格
  indentUnit.of('    '),
  // 添加搜索快捷键
  keymap.of(searchKeymap),
  // 添加历史记录快捷键（撤销/重做）
  keymap.of(historyKeymap),
  // 开启历史记录功能
  history(),
  // 开启搜索功能
  search(),
  // 开启代码括号匹配
  bracketMatching(),
  // 开启输入自动缩进
  indentOnInput(),
  // 开启代码折叠
  foldGutter(),
  // 显示行号
  lineNumbers(),
  // 高亮当前行的行号
  highlightActiveLineGutter(),
  // 语法检查器
  lintGutter(),
  // 自定义编辑器视图样式
  EditorView.theme({
    ".cm-scroller": { overflow: "auto" }
  })
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
    const response = await getModule(moduleId.value);
    if (response && response.data) {
      moduleInfo.value = response.data;
    } else {
      moduleInfo.value = {} as McpModuleInfo;
    }

    const toolsResponse = await getModuleTools(moduleId.value);
    if (toolsResponse && toolsResponse.data) {
      moduleTools.value = toolsResponse.data;
    } else {
      moduleTools.value = [];
    }

    // 默认选中第一个工具
    if (moduleTools.value.length > 0) {
      selectTool(moduleTools.value[0]);
    }

    // 如果模块有代码，初始化编辑器内容
    if (moduleInfo.value.code) {
      codeContent.value = moduleInfo.value.code;
      originalCode.value = moduleInfo.value.code;
    }

    // 处理config_schema
    if (moduleInfo.value.config_schema) {
      try {
        // 先确保config_schema是对象格式
        let schema: Record<string, any>;
        if (typeof moduleInfo.value.config_schema === 'string') {
          schema = JSON.parse(moduleInfo.value.config_schema);
        } else {
          schema = moduleInfo.value.config_schema;
        }

        Object.entries(schema).forEach(([key, config]: [string, any]) => {
          configParams.value.push({
            key,
            type: config.type || 'string',
            title: config.title || '',
            description: config.description || '',
            required: config.required || false,
            placeholder: config.placeholder || '',
            default: config.default
          });
        });
      } catch (e) {
        console.error('解析配置模式失败', e);
        ElMessage.error('配置模式解析失败');
      }
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

    // 直接使用marketplace API中提供的testModuleFunction方法
    const data = await testModuleFunction(moduleId, toolName, params);
    testResult.value = data.data;
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

  // 检查权限
  if (!hasEditPermission.value) {
    ElMessageBox.alert(
      '您没有权限编辑此MCP服务代码。只有管理员或服务创建者才能编辑。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

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
function handleEditorCreated(payload: { view: EditorView }) {
  const { view } = payload;
  // 可以在这里对编辑器进行其他初始化设置
  console.log('CodeMirror editor created', view);
}

// 格式化Python代码
function formatPythonCode() {
}

// 服务相关
const services = ref<McpServiceInfo[]>([]);
const loadingServices = ref(false);

// 是否有运行中的服务
const hasRunningService = computed(() => {
  return services.value.some(s => s.status === 'running');
});

// 加载服务列表
const loadServices = async () => {
  loadingServices.value = true;
  try {
    const response = await listServices(moduleId.value);
    if (response && response.data) {
      services.value = response.data;
    } else {
      services.value = [];
    }
  } catch (error) {
    console.error('加载服务列表失败', error);
    ElMessage.error('加载服务列表失败');
  } finally {
    loadingServices.value = false;
  }
};

// 服务发布相关
const publishDialogVisible = ref(false);
const configFormRef = ref<any>();
const configForm = ref<Record<string, any>>({});
const configRules = ref<Record<string, any>>({});
const publishing = ref(false);

// 判断是否有配置模式
const hasConfigSchema = computed(() => {
  return moduleInfo.value.config_schema &&
    Object.keys(moduleInfo.value.config_schema).length > 0;
});

// 初始化配置表单
function initConfigForm() {
  configForm.value = {
    service_name: `${moduleInfo.value.name}-实例-${new Date().getTime().toString().slice(-6)}` // 默认服务名称
  };
  configRules.value = {
    service_name: [{ required: true, message: '请输入服务名称', trigger: 'blur' }]
  };

  if (moduleInfo.value.config_schema) {
    Object.entries(moduleInfo.value.config_schema).forEach(([key, schema]: [string, any]) => {
      configForm.value[key] = '';
      if (schema.required) {
        configRules.value[key] = [
          { required: true, message: `请输入${schema.title || key}`, trigger: 'blur' }
        ];
      }
    });
  }
}

// 处理发布服务
const handlePublishService = () => {
  // 如果有配置参数，则显示配置对话框
  if (hasConfigSchema.value) {
    initConfigForm();
  }
  publishDialogVisible.value = true;
  //  else {
  //   // 否则直接发布
  //   publishServiceWithConfig({});
  // }
};

// 提交配置表单
const submitConfigForm = async () => {
  if (!configFormRef.value) return;

  try {
    await configFormRef.value.validate();
    publishDialogVisible.value = false;
    publishServiceWithConfig(configForm.value);
  } catch (error) {
    console.error('表单验证失败', error);
  }
};

// 带配置参数发布服务
const publishServiceWithConfig = async (config: Record<string, any>) => {
  try {
    ElMessage.info({ message: '正在发布服务...', duration: 0 });
    await publishModule(moduleId.value, config);
    ElMessage.closeAll();
    ElMessage.success('服务发布成功');
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    ElMessage.error(`发布服务失败: ${error.message || '未知错误'}`);
  }
};

// 停止服务
const handleStopService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在停止服务...', duration: 0 });
    await stopService(serviceUuid);
    ElMessage.closeAll();
    ElMessage.success('服务已停止');
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    ElMessage.error(`停止服务失败: ${error.message || '未知错误'}`);
  }
};

// 启动服务
const handleStartService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在启动服务...', duration: 0 });
    await startService(serviceUuid);
    ElMessage.closeAll();
    ElMessage.success('服务已启动');
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    ElMessage.error(`启动服务失败: ${error.message || '未知错误'}`);
  }
};

// 卸载服务
const handleUninstallService = async (serviceUuid: string) => {
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
      '确定要卸载此服务吗？卸载后将无法恢复。',
      '确认卸载',
      {
        confirmButtonText: '确认卸载',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    ElMessage.info({ message: '正在卸载服务...', duration: 0 });
    await uninstallService(serviceUuid);
    ElMessage.closeAll();
    ElMessage.success('服务已卸载');
    // 重新加载服务列表
    await loadServices();
  } catch (error: any) {
    ElMessage.closeAll();
    if (error !== 'cancel') {
      ElMessage.error(`卸载服务失败: ${error.message || '未知错误'}`);
    }
  }
};

// 复制URL到剪贴板
const copyUrl = (url: string) => {
  copyTextToClipboard(url, 'URL已复制到剪贴板');
};

// 复制为egovakb格式的URL
const copyAsEgovakbUrl = (url: string) => {
  // 创建egovakb格式的JSON
  const egovakbFormat = JSON.stringify({
    "mcp-sse": {
      "url": url,
      "transport": "sse"
    }
  }, null, 2);

  // 复制到剪贴板
  copyTextToClipboard(egovakbFormat, 'egovakb格式URL已复制到剪贴板');
};

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'running':
      return 'success';
    case 'stopped':
      return 'warning';
    case 'error':
      return 'danger';
    default:
      return 'info';
  }
};

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中';
    case 'stopped':
      return '已停止';
    case 'error':
      return '错误';
    default:
      return status;
  }
};

// 添加编辑相关的变量
const editDialogVisible = ref(false);
const updating = ref(false);
const categories = ref<McpCategoryInfo[]>([]);
const editFormRef = ref<any>();
const editForm = ref<{
  name: string;
  description: string;
  module_path: string;
  author: string;
  version: string;
  tags: string[];
  category_id: number | undefined;
  code: string;
  is_public: boolean;
  markdown_docs: string;
}>({
  name: '',
  description: '',
  module_path: '',
  author: '',
  version: '',
  tags: [],
  category_id: undefined,
  code: '',
  is_public: true,
  markdown_docs: ''
});

const editRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入服务描述', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入代码', trigger: 'blur' }
  ]
};

// 当前用户信息
const currentUser = ref<{
  user_id: number | null;
  username: string;
  is_admin: boolean;
}>({
  user_id: null,
  username: '',
  is_admin: false
});

// 加载用户信息
const loadUserInfo = () => {
  try {
    const userInfoStr = localStorage.getItem('userInfo');
    if (userInfoStr) {
      const userInfo = JSON.parse(userInfoStr);
      currentUser.value = {
        user_id: userInfo.user_id || null,
        username: userInfo.username || '',
        is_admin: userInfo.is_admin || false
      };
    }
  } catch (error) {
    console.error('获取用户信息失败', error);
  }
};

// 检查是否有编辑权限
const hasEditPermission = computed(() => {
  // 如果是管理员，有编辑权限
  if (currentUser.value.is_admin) {
    return true;
  }

  // 非管理员只能编辑自己创建的MCP服务
  return moduleInfo.value.user_id === currentUser.value.user_id;
});

// 配置参数相关
const configParams = ref<{
  key: string;
  type: string;
  title: string;
  description: string;
  required: boolean;
  placeholder?: string;
  default?: any;
}[]>([]);

// 添加配置参数
function addConfigParam() {
  configParams.value.push({
    key: '',
    type: 'string',
    title: '',
    description: '',
    required: false,
    placeholder: ''
  });
}

// 删除配置参数
function removeConfigParam(index: number) {
  configParams.value.splice(index, 1);
}

// 生成config_schema对象
function generateConfigSchema(): Record<string, any> {
  const schema: Record<string, any> = {};

  configParams.value.forEach(param => {
    if (!param.key) return;

    schema[param.key] = {
      type: param.type,
      description: param.description,
      required: param.required
    };

    if (param.title) {
      schema[param.key].title = param.title;
    }

    if (param.placeholder && (param.type === 'string' || param.type === 'password')) {
      schema[param.key].placeholder = param.placeholder;
    }

    if (param.default !== undefined && param.default !== null) {
      schema[param.key].default = param.default;
    }
  });

  return schema;
}

// 显示编辑对话框
function showEditDialog() {
  // 检查权限
  if (!hasEditPermission.value) {
    ElMessageBox.alert(
      '您没有权限编辑此MCP服务。只有管理员或服务创建者才能编辑。',
      '权限不足',
      { type: 'warning' }
    );
    return;
  }

  // 加载分类数据
  loadCategories();

  // 处理tags，确保是数组
  let tagsArray: string[] = [];
  if (typeof moduleInfo.value.tags === 'string') {
    tagsArray = moduleInfo.value.tags.split(',').filter(t => t.trim());
  } else if (Array.isArray(moduleInfo.value.tags)) {
    tagsArray = moduleInfo.value.tags;
  }

  // 处理配置参数
  configParams.value = [];
  if (moduleInfo.value.config_schema) {
    // 将配置转换为参数列表
    Object.entries(moduleInfo.value.config_schema).forEach(([key, config]: [string, any]) => {
      configParams.value.push({
        key,
        type: config.type || 'string',
        title: config.title || '',
        description: config.description || '',
        required: config.required || false,
        placeholder: config.placeholder || '',
        default: config.default
      });
    });
  }

  // 填充表单数据，确保每个字段都有默认值
  editForm.value = {
    name: moduleInfo.value.name || '',
    description: moduleInfo.value.description || '',
    module_path: moduleInfo.value.module_path || '',
    author: moduleInfo.value.author || '',
    version: moduleInfo.value.version || '',
    tags: tagsArray,
    category_id: moduleInfo.value.category_id || undefined,
    code: moduleInfo.value.code || '',
    is_public: moduleInfo.value.is_public === false ? false : true,
    markdown_docs: moduleInfo.value.markdown_docs || ''
  };

  nextTick(() => {
    editDialogVisible.value = true;
  });
}

// 加载分类列表
async function loadCategories() {
  try {
    const response = await listCategories();
    if (response && response.data) {
      categories.value = response.data;
    } else {
      categories.value = [];
    }
  } catch (error) {
    console.error("加载分类失败", error);
    ElNotification({
      title: '错误',
      message: '加载MCP分类列表失败',
      type: 'error'
    });
  }
}

// 提交编辑表单
async function submitEditForm() {
  updating.value = true;
  try {
    // 处理tags，转换为字符串
    const tagsStr = Array.isArray(editForm.value.tags) ? editForm.value.tags.join(',') : '';

    // 构建要更新的数据
    const moduleData: Partial<McpModuleInfo> = {
      name: editForm.value.name,
      description: editForm.value.description,
      module_path: editForm.value.module_path,
      author: editForm.value.author,
      version: editForm.value.version,
      tags: tagsStr,
      category_id: editForm.value.category_id,
      code: editForm.value.code,
      is_public: Boolean(editForm.value.is_public),
      markdown_docs: editForm.value.markdown_docs,
      config_schema: generateConfigSchema()
    };

    const response = await updateModule(moduleInfo.value.id, moduleData);

    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: 'MCP服务更新成功',
        type: 'success'
      });
      editDialogVisible.value = false;

      // 重新加载模块详情
      loadModuleInfo();
    } else {
      ElNotification({
        title: '错误',
        message: response?.message || '更新MCP服务失败',
        type: 'error'
      });
    }
  } catch (error) {
    console.error('更新MCP服务失败:', error);
    ElNotification({
      title: '错误',
      message: '更新MCP服务失败',
      type: 'error'
    });
  } finally {
    updating.value = false;
  }
}

// 处理删除模块
async function handleDeleteModule() {
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
      '确定要删除此MCP服务吗？删除后将无法恢复，其关联的所有服务也将被卸载。',
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    ElMessage.info({ message: '正在删除服务...', duration: 0 });
    const response = await deleteModule(moduleId.value);
    ElMessage.closeAll();
    if (response && response.code === 0) {
      ElMessage.success('服务已删除');
      // 删除成功后，返回到广场页面
      router.push('/marketplace');
    } else {
      ElMessage.error(`删除服务失败: ${response?.message || '未知错误'}`);
    }
  } catch (error: any) {
    ElMessage.closeAll();
    if (error !== 'cancel') {
      ElMessage.error(`删除服务失败: ${error.message || '未知错误'}`);
    }
  }
}

// 服务参数对话框相关
const serviceParamsDialogVisible = ref(false);
const currentService = ref<McpServiceInfo | null>(null);
const serviceParamsForm = ref<Record<string, any>>({});
const updatingParams = ref(false);

// 查看服务参数
const viewServiceParams = async (service: McpServiceInfo) => {
  try {
    // 获取最新的服务信息
    const response = await getService(service.service_uuid);
    if (response && response.data) {
      currentService.value = response.data;
      // 初始化表单
      serviceParamsForm.value = { ...response.data.config_params };
      serviceParamsDialogVisible.value = true;
    }
  } catch (error) {
    console.error('获取服务参数失败', error);
    ElMessage.error('获取服务参数失败');
  }
};

// 获取参数显示名称
const getParamDisplay = (key: string): string => {
  if (!moduleInfo.value.config_schema) return key;

  const schema = moduleInfo.value.config_schema[key];
  if (schema && schema.title) {
    return schema.title;
  }
  return key;
};

// 判断值类型
const isNumeric = (value: any): boolean => {
  return typeof value === 'number';
};

const isBoolean = (value: any): boolean => {
  return typeof value === 'boolean';
};

const isPassword = (key: string): boolean => {
  if (!moduleInfo.value.config_schema) return false;

  const schema = moduleInfo.value.config_schema[key];
  return schema && schema.type === 'password';
};

// 更新服务参数
const updateServiceParamsFunc = async () => {
  if (!currentService.value) return;

  updatingParams.value = true;
  try {
    // 调用API更新服务参数
    await updateServiceParams(currentService.value.id, serviceParamsForm.value);
    ElMessage.success('服务参数更新成功');
    serviceParamsDialogVisible.value = false;

    // 重新加载服务列表
    await loadServices();
  } catch (error) {
    console.error('更新服务参数失败', error);
    ElMessage.error('更新服务参数失败');
  } finally {
    updatingParams.value = false;
  }
};

// 页面加载时获取模块详情
onMounted(() => {
  loadUserInfo(); // 加载用户信息
  loadModuleInfo();
  loadServices(); // 添加加载服务
});
</script>

<style scoped>
.module-info-card {
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  transition: all 0.3s ease;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff, #f8fcff);
}

.module-info-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12) !important;
  transform: translateY(-2px);
}

.module-info-meta {
  background: rgba(245, 250, 255, 0.7);
  padding: 12px 16px;
  border-radius: 12px;
  min-width: 220px;
  border: 1px solid rgba(220, 240, 255, 0.8);
}

.module-meta-item {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.module-meta-item strong {
  color: #303133;
  margin-right: 4px;
}

.return-btn {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.tag-item {
  border-radius: 20px;
  padding: 0 12px;
  height: 24px;
  line-height: 22px;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.tag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.tool-test-panel {
  max-width: 800px;
}

.code-editor {
  border-radius: 8px;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 14px;
  height: 500px;
  overflow: auto;
}

:deep(.cm-editor) {
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.cm-scroller) {
  overflow: auto;
  border-radius: 8px;
  max-height: 100%;
}

.code-editor-container {
  width: 100%;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.code-editor-wrapper {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  margin-top: 12px;
  background: rgba(30, 30, 30, 0.95);
  height: 500px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.code-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.editor-title {
  font-size: 18px;
  font-weight: 500;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

:deep(.cm-gutters) {
  background-color: rgba(45, 45, 45, 0.95);
  border-right: 1px solid rgba(80, 80, 80, 0.3);
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}

:deep(.cm-activeLineGutter) {
  background-color: rgba(70, 70, 70, 0.5);
}

:deep(.cm-activeLine) {
  background-color: rgba(60, 60, 60, 0.5);
}

:deep(.cm-content) {
  padding: 8px 0;
}

:deep(.cm-lineNumbers) {
  color: rgba(150, 150, 150, 0.7);
}

.markdown-content {
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 16px;
  border: 1px solid #eee;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.markdown-content:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
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

.mcp-tool-list {
  width: 400px;
  padding-right: 20px;
}

.tool-test-content {
  flex: 1;
  padding-left: 24px;
}

.tool-params-card {
  border-radius: 16px;
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

:deep(.el-input__inner) {
  border-radius: 10px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

.tabs-card {
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  overflow: hidden;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: rgba(235, 235, 235, 0.8);
}

:deep(.el-tabs__item) {
  transition: all 0.3s ease;
  padding: 0 20px;
  height: 46px;
  line-height: 46px;
}

:deep(.el-tabs__item.is-active) {
  font-weight: 600;
  color: #409eff;
  transform: translateY(-2px);
}

:deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, #409eff, #79bbff);
}

:deep(.el-tab-pane) {
  padding: 16px 8px;
}

:deep(.el-empty) {
  padding: 32px 0;
  border-radius: 16px;
  background: rgba(250, 250, 250, 0.5);
  transition: all 0.3s ease;
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

:deep(.cm-scroller::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(.cm-scroller::-webkit-scrollbar-thumb) {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

:deep(.cm-scroller::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(255, 255, 255, 0.3);
}

:deep(.cm-scroller::-webkit-scrollbar-track) {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-card {
  border-radius: 16px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  transition: all 0.3s ease;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff, #f8f9ff);
}

.service-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-2px);
}

:deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(235, 235, 235, 0.6);
  background: rgba(250, 252, 255, 0.7);
}

.service-actions {
  display: flex;
  align-items: center;
}

:deep(.el-table) {
  --el-table-border-color: rgba(235, 235, 235, 0.6);
  --el-table-header-bg-color: rgba(246, 248, 250, 0.6);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: rgba(246, 248, 250, 0.6);
  font-weight: 600;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background-color: rgba(240, 247, 255, 0.6);
}

:deep(.el-table .cell) {
  padding: 8px 12px;
}

.service-table {
  margin-top: 8px;
}

:deep(.service-table .el-input__inner) {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
  background-color: #f8f9fb;
}

:deep(.service-table .el-input__wrapper) {
  box-shadow: none;
  border: 1px solid #e0e3e9;
}

:deep(.service-table .el-input__wrapper:hover) {
  border-color: #c0c4cc;
}

.config-schema-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03) !important;
}

.config-params-container {
  width: 100%;
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #ebeef5;
}

:deep(.el-table) {
  --el-table-border-color: #ebeef5;
  --el-table-header-bg-color: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table thead th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

:deep(.el-table__row:hover > td) {
  background-color: #f5f9ff;
}

:deep(.el-empty) {
  padding: 20px 0;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.config-param-item {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  padding: 12px;
  transition: all 0.2s ease;
}

.config-param-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-color: #e6f1ff;
}
</style>