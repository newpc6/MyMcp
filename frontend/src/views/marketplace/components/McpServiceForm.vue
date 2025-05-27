<template>
  <div class="mcp-service-form">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="top">
      <el-form-item label="服务名称" prop="name">
        <el-input v-model.trim="form.name" placeholder="请输入服务名称" clearable></el-input>
      </el-form-item>

      <el-form-item label="服务描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入服务描述" clearable></el-input>
      </el-form-item>

      <el-form-item label="版本" prop="version">
        <el-input v-model.trim="form.version" placeholder="请输入版本号，例如：1.0.0" clearable></el-input>
      </el-form-item>

      <el-form-item label="分类" prop="category_id">
        <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%" clearable>
          <el-option v-for="category in categories" :key="category.id" :label="category.name"
            :value="category.id"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="服务详情">
        <div class="markdown-container">
          <div class="markdown-edit-area">
            <div class="edit-header">
              <span class="edit-title">编辑</span>
            </div>
            <el-input v-model="form.markdown_docs" type="textarea" :rows="12" placeholder="请输入服务详情（支持Markdown格式）"
              class="markdown-editor" style="font-family: monospace;"></el-input>
          </div>
          <div class="markdown-preview-area">
            <div class="preview-header">
              <span class="preview-title">预览</span>
            </div>
            <div class="markdown-preview">
              <div v-if="form.markdown_docs" class="markdown-content">
                <VueMarkdownRender :source="form.markdown_docs" class="markdown-body" />
              </div>
              <el-empty v-else description="暂无内容可预览" />
            </div>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="参数配置模板" prop="config_schema">
        <div class="config-schema-container">
          <div class="config-schema-table-area">
            <div class="table-header">
              <span class="table-title">参数配置 ({{ configParams.length }})</span>
              <el-button type="primary" size="small" @click="addConfigParam">
                <el-icon>
                  <Plus />
                </el-icon>
                添加参数
              </el-button>
            </div>

            <el-table :data="configParams" border style="width: 100%" class="config-params-table">
              <el-table-column prop="key" label="参数名" width="120">
                <template #default="{ row }">
                  <span>{{ row.key || '未设置' }}</span>
                </template>
              </el-table-column>

              <el-table-column prop="title" label="显示名称" width="120">
                <template #default="{ row }">
                  <span>{{ row.title || '未设置' }}</span>
                </template>
              </el-table-column>

              <el-table-column prop="type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getTypeTagType(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
                </template>
              </el-table-column>

              <el-table-column prop="required" label="必填" width="80">
                <template #default="{ row }">
                  <el-tag v-if="row.required" type="danger" size="small">是</el-tag>
                  <el-tag v-else type="info" size="small">否</el-tag>
                </template>
              </el-table-column>

              <el-table-column prop="description" label="描述" min-width="150">
                <template #default="{ row }">
                  <span>{{ row.description || '无描述' }}</span>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="160" fixed="right">
                <template #default="{ $index }">
                  <el-button type="primary" size="small" @click="editConfigParam($index)">
                    编辑
                  </el-button>
                  <el-button type="danger" size="small" @click="removeConfigParam($index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="configParams.length === 0" class="empty-params">
              <el-empty description="暂无参数配置" :image-size="60">
                <el-button type="primary" @click="addConfigParam">添加第一个参数</el-button>
              </el-empty>
            </div>
          </div>

          <!-- <div class="config-schema-preview-area">
            <div class="preview-header">
              <span class="preview-title">JSON Schema 预览</span>
            </div>
            <div class="config-schema-preview">
              <div v-if="generatedConfigSchema && Object.keys(generatedConfigSchema).length > 0" class="json-preview">
                <pre>{{ JSON.stringify(generatedConfigSchema, null, 2) }}</pre>
              </div>
              <div v-else class="preview-empty">
                <el-empty description="暂无配置参数" :image-size="60" />
              </div>
            </div>
          </div> -->
        </div>
      </el-form-item>

      <el-form-item label="代码" prop="code">
        <Codemirror v-model="form.code" :extensions="extensions" class="code-editor" :indent-with-tab="true"
          :tab-size="4" style="height: 400px;" />
      </el-form-item>

      <el-form-item label="访问权限">
        <el-radio-group v-model="form.is_public">
          <el-radio :value="true">公开</el-radio>
          <el-radio :value="false">私有</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <div class="form-actions">
      <slot name="actions"></slot>
    </div>

    <!-- 参数编辑弹窗 -->
    <el-dialog v-model="paramDialogVisible" :title="isEditingParam ? '编辑参数' : '添加参数'" width="600px"
      @close="resetParamForm">
      <el-form :model="currentParam" :rules="paramRules" ref="paramFormRef" label-width="100px">
        <el-form-item label="参数名" prop="key">
          <el-input v-model="currentParam.key" placeholder="请输入参数名 (英文，如：api_key)" />
        </el-form-item>

        <el-form-item label="显示名称" prop="title">
          <el-input v-model="currentParam.title" placeholder="请输入显示名称 (如：API密钥)" />
        </el-form-item>

        <el-form-item label="参数类型" prop="type">
          <el-select v-model="currentParam.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="integer" />
            <el-option label="密码" value="password" />
            <el-option label="布尔值" value="boolean" />
          </el-select>
        </el-form-item>

        <el-form-item label="是否必填">
          <el-switch v-model="currentParam.required" />
        </el-form-item>

        <el-form-item label="描述信息">
          <el-input v-model="currentParam.description" type="textarea" :rows="3" placeholder="请输入参数描述信息" />
        </el-form-item>

        <el-form-item label="占位符">
          <el-input v-model="currentParam.placeholder" placeholder="请输入输入提示文本" />
        </el-form-item>

        <el-form-item label="默认值">
          <el-input v-model="currentParam.default" placeholder="请输入默认值" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="paramDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveParam">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch, computed, nextTick } from 'vue';
import { Plus, Delete } from '@element-plus/icons-vue';
import VueMarkdownRender from 'vue-markdown-render';
import Codemirror from 'vue-codemirror6';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { keymap } from '@codemirror/view';
import { defaultKeymap } from '@codemirror/commands';
import { lintGutter } from '@codemirror/lint';
import { indentUnit } from '@codemirror/language';
import { indentWithTab } from '@codemirror/commands';
import { EditorView } from '@codemirror/view';
import { basicSetup } from 'codemirror';
import { lineNumbers, highlightActiveLineGutter } from '@codemirror/view';
import { searchKeymap, search } from '@codemirror/search';
import { history, historyKeymap } from '@codemirror/commands';
import { bracketMatching, indentOnInput, foldGutter } from '@codemirror/language';
import type { McpCategoryInfo } from '../../../types/marketplace';

const props = defineProps<{
  modelValue: {
    name: string;
    description: string;
    module_path?: string;
    author?: string;
    version: string;
    tags?: string[];
    category_id: number | null;
    code: string;
    is_public: boolean;
    markdown_docs?: string;
    config_schema?: string;
  };
  categories: McpCategoryInfo[];
  isSubmitting?: boolean;
  configSchema?: Object | string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void;
  (e: 'submit'): void;
  (e: 'cancel'): void;
  (e: 'format-code'): void;
}>();

const formRef = ref();
const form = ref({ ...props.modelValue });

// 参数编辑弹窗相关
const paramDialogVisible = ref(false);
const paramFormRef = ref();
const isEditingParam = ref(false);
const editingParamIndex = ref(-1);
const currentParam = ref({
  key: '',
  title: '',
  type: 'string',
  description: '',
  placeholder: '',
  default: '',
  required: false
});

// 配置参数列表
const configParams = ref<{
  key: string;
  title: string;
  type: string;
  description: string;
  placeholder: string;
  default: string;
  required: boolean;
}[]>([]);

// 表单验证规则
const rules = {
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

// 参数表单验证规则
const paramRules = {
  key: [
    { required: true, message: '请输入参数名', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '参数名只能包含字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入显示名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择参数类型', trigger: 'change' }
  ]
};

// CodeMirror 扩展配置
const extensions = [
  basicSetup,
  python(),
  oneDark,
  keymap.of(defaultKeymap),
  keymap.of([indentWithTab]),
  indentUnit.of('    '),
  keymap.of(searchKeymap),
  keymap.of(historyKeymap),
  history(),
  search(),
  bracketMatching(),
  indentOnInput(),
  foldGutter(),
  lineNumbers(),
  highlightActiveLineGutter(),
  lintGutter(),
  EditorView.theme({
    ".cm-scroller": { overflow: "auto" }
  })
];

// 生成配置 Schema
const generatedConfigSchema = computed(() => {
  const schema: Record<string, any> = {};
  console.log('generatedConfigSchema', configParams.value)
  configParams.value.forEach(param => {
    if (!param.key) return;

    schema[param.key] = {
      type: param.type,
      title: param.title,
      description: param.description,
      required: param.required
    };

    if (param.placeholder) {
      schema[param.key].placeholder = param.placeholder;
    }

    if (param.default) {
      schema[param.key].default = param.default;
    }
  });

  return schema;
});

// 添加配置参数
const addConfigParam = () => {
  resetParamForm();
  isEditingParam.value = false;
  paramDialogVisible.value = true;
};

// 编辑配置参数
const editConfigParam = (index: number) => {
  const param = configParams.value[index];
  currentParam.value = { ...param };
  editingParamIndex.value = index;
  isEditingParam.value = true;
  paramDialogVisible.value = true;
};

// 移除配置参数
const removeConfigParam = (index: number) => {
  configParams.value.splice(index, 1);
  updateConfigSchema();
};

// 保存参数
const saveParam = async () => {
  console.log('saveParam', currentParam.value)
  try {
    await paramFormRef.value?.validate();

    if (isEditingParam.value) {
      // 编辑模式
      configParams.value[editingParamIndex.value] = { ...currentParam.value };
    } else {
      // 新增模式
      configParams.value.push({ ...currentParam.value });
    }

    updateConfigSchema();
    paramDialogVisible.value = false;
    resetParamForm();
  } catch (error) {
    console.error('参数验证失败:', error);
  }
};

// 重置参数表单
const resetParamForm = () => {
  currentParam.value = {
    key: '',
    title: '',
    type: 'string',
    description: '',
    placeholder: '',
    default: '',
    required: false
  };
  editingParamIndex.value = -1;
  paramFormRef.value?.resetFields();
};

// 获取类型标签样式
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    string: '',
    integer: 'success',
    password: 'warning',
    boolean: 'info'
  };
  return typeMap[type] || '';
};

// 获取类型显示标签
const getTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    string: '字符串',
    integer: '整数',
    password: '密码',
    boolean: '布尔值'
  };
  return labelMap[type] || type;
};

// 更新配置 Schema
const updateConfigSchema = () => {
  const newSchema = JSON.stringify(generatedConfigSchema.value, null, 2);
  if (form.value.config_schema !== newSchema) {
    form.value.config_schema = newSchema;
  }
};

// 初始化配置参数
const initConfigParams = () => {
  configParams.value = [];
  console.log('initConfigParams', form.value.config_schema)
  if (form.value.config_schema) {
    try {
      let schema;
      
      // 处理不同格式的 config_schema
      if (typeof form.value.config_schema === 'string') {
        // 如果是字符串，尝试解析为 JSON
        schema = JSON.parse(form.value.config_schema);
      } else if (typeof form.value.config_schema === 'object') {
        // 如果已经是对象，直接使用
        schema = form.value.config_schema;
      } else {
        console.warn('config_schema 格式不正确:', form.value.config_schema);
        return;
      }
      
      // 将对象转换为参数列表
      Object.entries(schema).forEach(([key, config]: [string, any]) => {
        configParams.value.push({
          key,
          title: config.title || '',
          type: config.type || 'string',
          description: config.description || '',
          placeholder: config.placeholder || '',
          default: config.default || '',
          required: config.required || false
        });
      });
      
      console.log('initConfigParams 2', configParams.value)
    } catch (error) {
      console.error('解析配置 Schema 失败:', error);
    }
  }
};

// 监听表单数据变化，同步到父组件
watch(form, (newVal) => {
  emit('update:modelValue', newVal);
  console.log('form', newVal)
}, { deep: true });

// 监听 props 变化，初始化配置参数
watch(() => props.modelValue, (newVal, oldVal) => {
  console.log('props.modelValue', newVal)
  
  // 深度比较，避免不必要的更新
  const newStr = JSON.stringify(newVal);
  const oldStr = JSON.stringify(oldVal);
  
  if (newStr !== oldStr) {
    form.value = { ...newVal };
    nextTick(() => {
      initConfigParams();
    });
  }
}, { immediate: true });

// 暴露表单验证方法给父组件
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
});
</script>

<style scoped>
.mcp-service-form {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.markdown-container {
  display: flex;
  gap: 16px;
  width: 100%;
  min-height: 300px;
}

/* 响应式布局 */
@media (max-width: 992px) {
  .markdown-container {
    flex-direction: column;
  }

  .markdown-edit-area,
  .markdown-preview-area {
    width: 100%;
  }

  .markdown-preview {
    min-height: 200px;
  }
}

.markdown-edit-area,
.markdown-preview-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  overflow: hidden;
}

.edit-header,
.preview-header {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #DCDFE6;
}

.edit-title,
.preview-title {
  font-weight: 500;
  font-size: 14px;
  color: #606266;
}

.markdown-editor {
  width: 100%;
  border: none;
  border-radius: 0;
  height: 100%;
  min-height: 300px;
}

.markdown-preview {
  min-height: 300px;
  padding: 16px;
  background-color: #fff;
  overflow-y: auto;
  height: 100%;
}

:deep(.el-textarea__inner) {
  border: none;
  resize: none;
  height: 100% !important;
  min-height: 300px;
}

.markdown-content {
  padding: 0.5rem;
}

:deep(.markdown-body) {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

:deep(.markdown-body h1),
:deep(.markdown-body h2),
:deep(.markdown-body h3),
:deep(.markdown-body h4) {
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  font-weight: 600;
}

:deep(.markdown-body h1) {
  font-size: 2em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

:deep(.markdown-body h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
}

:deep(.markdown-body h3) {
  font-size: 1.25em;
}

:deep(.markdown-body h4) {
  font-size: 1em;
}

:deep(.markdown-body p) {
  margin-bottom: 1em;
}

:deep(.markdown-body ul),
:deep(.markdown-body ol) {
  padding-left: 2em;
  margin-bottom: 1em;
}

:deep(.markdown-body li) {
  margin-bottom: 0.5em;
}

:deep(.markdown-body code) {
  font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

:deep(.markdown-body pre) {
  background-color: #f6f8fa;
  border-radius: 3px;
  padding: 1em;
  overflow: auto;
  margin-bottom: 1em;
}

:deep(.markdown-body pre code) {
  background-color: transparent;
  padding: 0;
}

:deep(.markdown-body blockquote) {
  border-left: 0.25em solid #dfe2e5;
  padding: 0 1em;
  color: #6a737d;
  margin-bottom: 1em;
}

:deep(.markdown-body img) {
  max-width: 100%;
  height: auto;
}

:deep(.markdown-body table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}

:deep(.markdown-body table th),
:deep(.markdown-body table td) {
  border: 1px solid #dfe2e5;
  padding: 6px 13px;
}

:deep(.markdown-body table th) {
  background-color: #f6f8fa;
  font-weight: 600;
}

:deep(.code-editor) {
  border-radius: 8px;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 14px;
  height: 400px;
  overflow: auto;
  width: 100%;
}

:deep(.cm-editor) {
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  width: 100%;
}

:deep(.cm-scroller) {
  overflow: auto;
  border-radius: 8px;
  max-height: 100%;
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

.config-schema-container {
  display: flex;
  gap: 16px;
  width: 100%;
  min-height: 300px;
}

/* 响应式布局 */
@media (max-width: 992px) {
  .config-schema-container {
    flex-direction: column;
  }

  .config-schema-table-area,
  .config-schema-preview-area {
    width: 100%;
  }

  .config-schema-preview {
    min-height: 150px;
  }
}

.config-schema-table-area,
.config-schema-preview-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #DCDFE6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.table-title {
  font-weight: 500;
  font-size: 14px;
  color: #606266;
}

.config-params-table {
  width: 100%;
}

.config-schema-preview {
  min-height: 300px;
  padding: 16px;
  background-color: #fff;
  overflow-y: auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.json-preview {
  padding: 16px;
  background-color: #fff;
  overflow-y: auto;
  height: 100%;
}

.preview-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-icon {
  margin-left: 8px;
  color: #909399;
  cursor: help;
}

.edit-header .info-icon {
  margin-left: auto;
}

.edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.empty-params {
  padding: 20px;
  text-align: center;
}

.json-preview pre {
  margin: 0;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
  color: #333;
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

:deep(.config-params-table .el-table__cell) {
  padding: 8px 4px;
}

:deep(.config-params-table .el-input__wrapper) {
  box-shadow: none;
  border: 1px solid #dcdfe6;
}

:deep(.config-params-table .el-select) {
  width: 100%;
}

:deep(.config-params-table .el-button) {
  padding: 4px 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

.config-params-table .el-button+.el-button {
  margin-left: 8px;
}
</style>