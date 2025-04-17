<template>
  <div class="editor">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑模块: {{ modulePath }}</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button type="primary" @click="saveContent" :loading="saving">
              保存
            </el-button>
          </div>
        </div>
      </template>
      
      <div ref="editorContainer" class="editor-container"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMCPStore } from '@/store'
import * as monaco from 'monaco-editor'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useMCPStore()
const editorContainer = ref<HTMLElement | null>(null)
const editor = ref<monaco.editor.IStandaloneCodeEditor | null>(null)
const saving = ref(false)
const modulePath = ref('')

const goBack = () => {
  router.back()
}

const saveContent = async () => {
  if (!editor.value) return
  
  saving.value = true
  try {
    await store.updateModule(modulePath.value, editor.value.getValue())
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('Failed to save module:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  modulePath.value = route.params.path as string
  
  try {
    const response = await store.fetchModules()
    const module = response[modulePath.value]
    if (!module) {
      ElMessage.error('模块不存在')
      router.back()
      return
    }
    
    if (editorContainer.value) {
      editor.value = monaco.editor.create(editorContainer.value, {
        value: module.content,
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: {
          enabled: true
        }
      })
    }
  } catch (error) {
    console.error('Failed to load module:', error)
    ElMessage.error('加载模块失败')
    router.back()
  }
})

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.dispose()
  }
})
</script>

<style scoped>
.editor-container {
  height: calc(100vh - 200px);
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 