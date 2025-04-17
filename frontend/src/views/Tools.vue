<template>
  <div class="tools">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>MCP工具列表</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索工具..."
            style="width: 200px"
            clearable
          />
        </div>
      </template>
      
      <el-table :data="filteredTools" style="width: 100%">
        <el-table-column prop="name" label="工具名称" />
        <el-table-column prop="doc" label="描述" />
        <el-table-column prop="return_type" label="返回类型" width="120" />
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="scope">
            <el-button link type="primary" @click="showToolDialog(scope.row)">
              使用
            </el-button>
            <el-button link type="primary" @click="goToModule(scope.row.file_path)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog
      v-model="toolDialogVisible"
      :title="currentTool?.name"
      width="50%"
    >
      <div v-if="currentTool">
        <p>{{ currentTool.doc }}</p>
        
        <el-form
          ref="toolForm"
          :model="toolForm"
          label-width="120px"
          class="tool-form"
        >
          <el-form-item
            v-for="(param, name) in currentTool.parameters"
            :key="name"
            :label="name"
            :prop="name"
          >
            <el-input
              v-if="param.type === 'str'"
              v-model="toolForm[name]"
              :placeholder="`输入${name}`"
            />
            <el-input-number
              v-else-if="param.type === 'int'"
              v-model="toolForm[name]"
              :placeholder="`输入${name}`"
            />
            <el-input-number
              v-else-if="param.type === 'float'"
              v-model="toolForm[name]"
              :placeholder="`输入${name}`"
              :step="0.1"
            />
            <el-switch
              v-else-if="param.type === 'bool'"
              v-model="toolForm[name]"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="toolDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="executeTool" :loading="executing">
            执行
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="resultDialogVisible"
      title="执行结果"
      width="50%"
    >
      <pre class="result-content">{{ toolResult }}</pre>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resultDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMCPStore } from '@/store'
import type { FormInstance } from 'element-plus'

const store = useMCPStore()
const router = useRouter()
const searchQuery = ref('')
const toolDialogVisible = ref(false)
const resultDialogVisible = ref(false)
const currentTool = ref<any>(null)
const toolForm = ref<Record<string, any>>({})
const toolResult = ref('')
const executing = ref(false)
const toolFormRef = ref<FormInstance>()

const filteredTools = computed(() => {
  const tools = Object.values(store.tools)
  if (!searchQuery.value) return tools
  
  const query = searchQuery.value.toLowerCase()
  return tools.filter(tool => 
    tool.name.toLowerCase().includes(query) ||
    tool.doc.toLowerCase().includes(query)
  )
})

const showToolDialog = (tool: any) => {
  currentTool.value = tool
  toolForm.value = {}
  toolDialogVisible.value = true
}

const goToModule = (filePath: string) => {
  router.push({
    name: 'Editor',
    params: { path: filePath }
  })
}

const executeTool = async () => {
  if (!currentTool.value) return
  
  executing.value = true
  try {
    const result = await store.executeTool(
      currentTool.value.name,
      toolForm.value
    )
    toolResult.value = JSON.stringify(result, null, 2)
    resultDialogVisible.value = true
    toolDialogVisible.value = false
  } catch (error) {
    console.error('Failed to execute tool:', error)
  } finally {
    executing.value = false
  }
}

onMounted(() => {
  store.fetchTools()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tool-form {
  margin-top: 20px;
}

.result-content {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 