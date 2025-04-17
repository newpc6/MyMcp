<template>
  <div class="modules">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>MCP模块列表</span>
          <div>
            <el-input
              v-model="searchQuery"
              placeholder="搜索模块..."
              style="width: 200px; margin-right: 10px"
              clearable
            />
            <el-button type="primary" @click="showCreateDialog">
              新建模块
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredModules" style="width: 100%">
        <el-table-column prop="path" label="路径" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="scope">
            {{ formatSize(scope.row.size) }}
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="scope">
            <el-button link type="primary" @click="editModule(scope.row.path)">
              编辑
            </el-button>
            <el-button link type="danger" @click="deleteModule(scope.row.path)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog
      v-model="createDialogVisible"
      title="新建模块"
      width="50%"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="路径" prop="path">
          <el-input v-model="createForm.path" placeholder="例如: tools/new_tool.py" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="10"
            placeholder="输入模块内容..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createModule" :loading="creating">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMCPStore } from '@/store'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useMCPStore()
const router = useRouter()
const searchQuery = ref('')
const createDialogVisible = ref(false)
const creating = ref(false)
const createFormRef = ref<FormInstance>()

const createForm = ref({
  path: '',
  content: ''
})

const createRules: FormRules = {
  path: [
    { required: true, message: '请输入模块路径', trigger: 'blur' },
    { pattern: /\.py$/, message: '路径必须以.py结尾', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入模块内容', trigger: 'blur' }
  ]
}

const filteredModules = computed(() => {
  const modules = Object.values(store.modules)
  if (!searchQuery.value) return modules
  
  const query = searchQuery.value.toLowerCase()
  return modules.filter(module => 
    module.path.toLowerCase().includes(query)
  )
})

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const showCreateDialog = () => {
  createForm.value = {
    path: '',
    content: ''
  }
  createDialogVisible.value = true
}

const createModule = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      creating.value = true
      try {
        await store.createModule(createForm.value.path, createForm.value.content)
        ElMessage.success('模块创建成功')
        createDialogVisible.value = false
      } catch (error) {
        console.error('Failed to create module:', error)
        ElMessage.error('模块创建失败')
      } finally {
        creating.value = false
      }
    }
  })
}

const editModule = (path: string) => {
  router.push({
    name: 'Editor',
    params: { path }
  })
}

const deleteModule = async (path: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个模块吗？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await store.deleteModule(path)
    ElMessage.success('模块删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete module:', error)
      ElMessage.error('模块删除失败')
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 