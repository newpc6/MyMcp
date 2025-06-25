<template>
  <div class="scheduled-tasks-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon">
            <Timer />
          </el-icon>
          定时任务管理
        </h1>
        <p class="page-subtitle">查看和管理系统定时任务</p>
      </div>
      
      <div class="header-actions">
        <el-button @click="goBack" :icon="ArrowLeft">
          返回
        </el-button>
        <el-button type="primary" @click="loadScheduledTasks" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="tasks-container">
      <el-table
        :data="scheduledTasks"
        style="width: 100%"
        v-loading="loading"
        element-loading-text="加载定时任务..."
        empty-text="暂无定时任务"
      >
        <el-table-column prop="name" label="任务名称" min-width="150">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="任务描述" min-width="200" />
        
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getCategoryTagType(row.category)"
              size="small"
            >
              {{ row.category }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="interval" label="执行间隔" min-width="150" />
        
        <el-table-column prop="next_run" label="下次执行时间" min-width="180">
          <template #default="{ row }">
            <span class="task-execution-time">{{ row.next_run }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === '运行中' ? 'success' : 'warning'"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="executeTask(row)"
              :loading="executingTasks.includes(row.name)"
            >
              执行
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 任务统计卡片 -->
    <div class="stats-cards" v-if="scheduledTasks.length > 0">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ runningTasksCount }}</div>
          <div class="stat-label">运行中任务</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalTasksCount }}</div>
          <div class="stat-label">总任务数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon info">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ categoryCount }}</div>
          <div class="stat-label">任务分类</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Refresh, CircleCheck, Warning, Clock, ArrowLeft } from '@element-plus/icons-vue'
import { getScheduledTasks, executeScheduledTask, type ScheduledTask } from '../../api/system'

// 路由
const router = useRouter()

// 响应式数据
const scheduledTasks = ref<ScheduledTask[]>([])
const loading = ref(false)
const executingTasks = ref<string[]>([])

// 计算属性
const runningTasksCount = computed(() => {
  return scheduledTasks.value.filter(task => task.status === '运行中').length
})

const totalTasksCount = computed(() => {
  return scheduledTasks.value.length
})

const categoryCount = computed(() => {
  const categories = new Set(scheduledTasks.value.map(task => task.category))
  return categories.size
})

// 返回系统管理页面
const goBack = () => {
  router.push('/system')
}

// 加载定时任务列表
const loadScheduledTasks = async () => {
  loading.value = true
  try {
    const response = await getScheduledTasks()
    if (response.data && response.data.code === 0) {
      scheduledTasks.value = response.data.data || []
      ElMessage.success('定时任务列表加载成功')
    } else {
      ElMessage.error('获取定时任务列表失败')
      scheduledTasks.value = []
    }
  } catch (error) {
    console.error('获取定时任务列表失败:', error)
    ElMessage.error('获取定时任务列表失败')
    scheduledTasks.value = []
  } finally {
    loading.value = false
  }
}

// 执行定时任务
const executeTask = async (task: ScheduledTask) => {
  try {
    await ElMessageBox.confirm(
      `确认要立即执行任务 "${task.description}" 吗？`,
      '确认执行',
      {
        type: 'warning',
        confirmButtonText: '确认执行',
        cancelButtonText: '取消'
      }
    )

    executingTasks.value.push(task.name)
    
    const response = await executeScheduledTask(task.name)
    if (response.data && response.data.code === 0) {
      ElMessage.success(`任务 "${task.description}" 已开始执行`)
      // 刷新任务列表
      setTimeout(() => {
        loadScheduledTasks()
      }, 1000)
    } else {
      ElMessage.error(response.data?.message || '执行任务失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('执行任务失败:', error)
      ElMessage.error('执行任务失败')
    }
  } finally {
    const index = executingTasks.value.indexOf(task.name)
    if (index > -1) {
      executingTasks.value.splice(index, 1)
    }
  }
}

// 获取分类标签类型
const getCategoryTagType = (category: string) => {
  switch (category) {
    case '统计':
      return 'primary'
    case '清理':
      return 'warning'
    case '系统':
      return 'success'
    default:
      return 'info'
  }
}

// 页面挂载时加载数据
onMounted(() => {
  loadScheduledTasks()
})
</script>

<style scoped>
.scheduled-tasks-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.title-icon {
  color: #3b82f6;
}

.page-subtitle {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.tasks-container {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.task-execution-time {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #6b7280;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: #f0f9ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #3b82f6;
}

.stat-icon.warning {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-icon.info {
  background: #f0f4ff;
  color: #6366f1;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.stat-label {
  color: #6b7280;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .scheduled-tasks-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-end;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style> 