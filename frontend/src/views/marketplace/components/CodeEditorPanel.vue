<template>
  <div class="code-editor-container">
    <div v-if="!code" class="p-4">
      <el-empty description="该模块暂无代码" />
    </div>
    <div v-else>
      <div class="code-editor-header">
        <h3 class="editor-title">模块代码</h3>
        <div class="editor-actions">
          <el-alert v-if="!hasEditPermission" type="warning" :closable="false" show-icon title="您只能查看代码，没有编辑权限"
            class="mr-4" />
          <el-button type="primary" size="small" @click="$emit('format')" :loading="saving" v-if="hasEditPermission">
            格式化代码
          </el-button>
          <el-button type="primary" size="small" @click="$emit('save')" :loading="saving" :disabled="!hasCodeChanged"
            v-if="hasEditPermission">
            保存修改
          </el-button>
        </div>
      </div>
      <div class="code-editor-wrapper">
        <Codemirror v-model="internalCode" :extensions="extensions" class="code-editor" :indent-with-tab="true"
          :tab-size="4" @ready="handleEditorCreated" style="overflow: auto; height: 100%;"
          :readonly="!hasEditPermission" basic />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue';
import Codemirror from 'vue-codemirror6';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
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

const props = defineProps<{
  modelValue: string;
  originalCode: string;
  hasEditPermission: boolean;
  saving: boolean;
  code: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'save'): void;
  (e: 'format'): void;
}>();

// 创建内部的代码内容ref，用于双向绑定
const internalCode = ref(props.modelValue || '');

// 监听props.modelValue变化，同步到内部ref
watch(() => props.modelValue, (newValue) => {
  const newCode = typeof newValue === 'string' ? newValue : '';
  if (internalCode.value !== newCode) {
    internalCode.value = newCode;
  }
}, { immediate: true });

// 监听内部ref变化，触发emit
watch(internalCode, (newValue) => {
  if (newValue !== props.modelValue) {
    emit('update:modelValue', newValue);
  }
});

// 判断代码是否有变化
const hasCodeChanged = computed(() => {
  // 确保两个值都是字符串类型
  const currentCode = typeof internalCode.value === 'string' ? internalCode.value : '';
  const originalCodeStr = typeof props.originalCode === 'string' ? props.originalCode : '';
  
  const changed = currentCode !== originalCodeStr;
  
  return changed;
});

// 监听代码变化状态，用于调试
watch([hasCodeChanged, () => props.hasEditPermission], ([codeChanged, editPermission]) => {
  console.log('📊 保存按钮状态:', {
    hasCodeChanged: codeChanged,
    hasEditPermission: editPermission,
    saveButtonEnabled: codeChanged && editPermission,
    currentCodeLength: internalCode.value?.length || 0,
    originalCodeLength: props.originalCode?.length || 0
  });
}, { immediate: true });

// 监听internalCode变化，确保v-model正常工作
watch(internalCode, (newValue, oldValue) => {
  console.log('🔄 InternalCode变化:', {
    newValue: newValue?.substring(0, 50) + (newValue && newValue.length > 50 ? '...' : ''),
    oldValue: oldValue?.substring(0, 50) + (oldValue && oldValue.length > 50 ? '...' : ''),
    newValueLength: newValue?.length || 0,
    oldValueLength: oldValue?.length || 0
  });
}, { immediate: true });

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

// 在代码编辑页面中添加编辑器扩展配置
function handleEditorCreated(payload: { view: EditorView }) {
  const { view } = payload;
  // 可以在这里对编辑器进行其他初始化设置
}
</script>

<script lang="ts">
export default {
  name: 'CodeEditorPanel'
}
</script>

<style scoped>
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