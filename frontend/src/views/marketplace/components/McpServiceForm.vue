<template>
  <div class="mcp-service-form">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="top">
      <el-form-item label="服务名称" prop="name">
        <el-input v-model.trim="form.name" placeholder="请输入服务名称" clearable></el-input>
      </el-form-item>

      <el-form-item label="服务描述" prop="description">
        <el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入服务描述" clearable></el-input>
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
            <el-input v-model="form.markdown_docs" type="textarea" rows="12" placeholder="请输入服务详情（支持Markdown格式）" 
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

      <el-form-item label="代码" prop="code">
        <Codemirror v-model="form.code" :extensions="extensions" class="code-editor" 
          :indent-with-tab="true" :tab-size="4" style="height: 400px;" />
      </el-form-item>

      <el-form-item label="访问权限">
        <el-radio-group v-model="form.is_public">
          <el-radio :label="true">公开</el-radio>
          <el-radio :label="false">私有</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <div class="form-actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue';
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
  };
  categories: McpCategoryInfo[];
  isSubmitting?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void;
  (e: 'submit'): void;
  (e: 'cancel'): void;
  (e: 'format-code'): void;
}>();

const formRef = ref();
const form = ref({ ...props.modelValue });

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

// 监听表单数据变化，同步到父组件
watch(form, (newVal) => {
  emit('update:modelValue', newVal);
}, { deep: true });

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

.markdown-edit-area, .markdown-preview-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  overflow: hidden;
}

.edit-header, .preview-header {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #DCDFE6;
}

.edit-title, .preview-title {
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
</style> 