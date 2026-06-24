<template>
  <div>
    <div v-if="moduleInfo.markdown_docs" class="markdown-content mb-6">
      <VueMarkdownRender :source="moduleInfo.markdown_docs" class="markdown-body" />
    </div>

    <el-empty v-else description="没有找到详细文档" />
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import VueMarkdownRender from 'vue-markdown-render';
import type { McpModuleInfo } from '../../../types/marketplace';

defineProps<{
  moduleInfo: McpModuleInfo;
}>();
</script>

<script lang="ts">
export default {
  name: 'ServiceDetailsPanel'
}
</script>

<style scoped>
.markdown-content {
  padding: 16px;
  background-color: var(--common-panel-background-color);
  border-radius: var(--common-radius-lg);
  border: 1px solid var(--common-border-color);
  box-shadow: var(--common-shadow-xs);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.markdown-content:hover {
  box-shadow: var(--common-shadow-xs);
  transform: none;
}

.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: var(--common-text-color);
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
