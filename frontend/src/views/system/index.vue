<template>
  <div class="system-management">
    <div class="header">
      <h1>系统管理</h1>
      <p>管理系统配置、Python环境及相关服务</p>
    </div>

    <div class="management-grid">
      <div class="management-card" @click="$router.push('/system/python-packages')">
        <div class="card-icon">
          <i class="icon-python"></i>
        </div>
        <div class="card-content">
          <h3>Python包管理</h3>
          <p>安装、卸载和管理Python第三方库</p>
        </div>
        <div class="card-arrow">
          <i class="arrow-right"></i>
        </div>
      </div>

      <div class="management-card" @click="$router.push('/system/scheduled-tasks')">
        <div class="card-icon">
          <i class="icon-schedule"></i>
        </div>
        <div class="card-content">
          <h3>定时任务管理</h3>
          <p>查看和管理系统定时任务</p>
        </div>
        <div class="card-arrow">
          <i class="arrow-right"></i>
        </div>
      </div>

      <div class="management-card" @click="handleLogManagement">
        <div class="card-icon">
          <i class="icon-log"></i>
        </div>
        <div class="card-content">
          <h3>日志管理</h3>
          <p>查看和管理系统运行日志</p>
        </div>
        <div class="card-arrow">
          <i class="arrow-right"></i>
        </div>
      </div>
    </div>

    <!-- 定时任务对话框 -->
    <el-dialog
      v-model="scheduledTasksDialogVisible"
      title="定时任务管理"
      width="80%"
      :before-close="handleCloseTasksDialog"
    >
      <div class="scheduled-tasks-container">
        <div class="tasks-header">
          <el-button type="primary" @click="loadScheduledTasks" :loading="tasksLoading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <el-table
          :data="scheduledTasks"
          style="width: 100%"
          v-loading="tasksLoading"
          element-loading-text="加载定时任务..."
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
          <el-table-column prop="next_run" label="下次执行时间" min-width="180" />
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
    </el-dialog>

    <div class="system-status">
      <h2>系统状态</h2>
      
      <!-- 基础信息 -->
      <div class="status-section">
        <h3>基础信息</h3>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-label">Python版本:</span>
            <span class="status-value">{{ systemInfo.pythonVersion }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">系统运行时间:</span>
            <span class="status-value">{{ systemInfo.uptime }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">MCP服务状态:</span>
            <span class="status-value" :class="{ 'status-online': systemInfo.mcpStatus === 'running' }">
              {{ systemInfo.mcpStatus }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">操作系统:</span>
            <span class="status-value">{{ systemInfo.platform }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">系统架构:</span>
            <span class="status-value">{{ systemInfo.architecture }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">处理器:</span>
            <span class="status-value">{{ systemInfo.processor }}</span>
          </div>
        </div>
      </div>

      <!-- 内存使用情况 -->
      <div class="status-section">
        <h3>内存使用情况</h3>
        <div class="resource-info">
          <div class="resource-header">
            <span>{{ formatBytes(systemInfo.memory?.used || 0) }} / {{ formatBytes(systemInfo.memory?.total || 0) }}</span>
            <span class="percentage">{{ systemInfo.memory?.percent || 0 }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: (systemInfo.memory?.percent || 0) + '%' }"></div>
          </div>
          <div class="resource-details">
            <div class="detail-item">
              <span>已用: {{ formatBytes(systemInfo.memory?.used || 0) }}</span>
            </div>
            <div class="detail-item">
              <span>可用: {{ formatBytes(systemInfo.memory?.available || 0) }}</span>
            </div>
            <div class="detail-item">
              <span>总计: {{ formatBytes(systemInfo.memory?.total || 0) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 磁盘使用情况 -->
      <div class="status-section">
        <h3>磁盘使用情况</h3>
        <div class="resource-info">
          <div class="resource-header">
            <span>{{ formatBytes(systemInfo.disk?.used || 0) }} / {{ formatBytes(systemInfo.disk?.total || 0) }}</span>
            <span class="percentage">{{ systemInfo.disk?.percent || 0 }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill disk" :style="{ width: (systemInfo.disk?.percent || 0) + '%' }"></div>
          </div>
          <div class="resource-details">
            <div class="detail-item">
              <span>已用: {{ formatBytes(systemInfo.disk?.used || 0) }}</span>
            </div>
            <div class="detail-item">
              <span>可用: {{ formatBytes(systemInfo.disk?.free || 0) }}</span>
            </div>
            <div class="detail-item">
              <span>总计: {{ formatBytes(systemInfo.disk?.total || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getSystemInfo, getScheduledTasks, executeScheduledTask, type ScheduledTask } from '../../api/system'

const router = useRouter()

// 系统信息
const systemInfo = ref({
  pythonVersion: '加载中...',
  uptime: '加载中...',
  mcpStatus: '检查中...',
  platform: '加载中...',
  architecture: '加载中...',
  processor: '加载中...',
  memory: {
    total: 0,
    available: 0,
    used: 0,
    percent: 0
  },
  disk: {
    total: 0,
    used: 0,
    free: 0,
    percent: 0
  }
})

// 定时任务相关
const scheduledTasksDialogVisible = ref(false)
const scheduledTasks = ref<ScheduledTask[]>([])
const tasksLoading = ref(false)
const executingTasks = ref<string[]>([])

// 格式化字节数为可读格式
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const loadSystemInfo = async () => {
  try {
    const response = await getSystemInfo()
    
    // 检查响应格式并正确提取数据
    if (response.data && response.data.code === 0) {
      systemInfo.value = response.data.data
    } else if (response.data) {
      systemInfo.value = response.data
    } else {
      console.error('获取系统信息失败:', response.data?.message)
      // 如果API调用失败，使用模拟数据
      systemInfo.value = {
        pythonVersion: '3.11.0',
        uptime: '2天 5小时 30分钟',
        mcpStatus: 'running',
        platform: 'Windows-10-10.0.26100-SP0',
        architecture: '64bit',
        processor: 'Intel64 Family 6 Model 183 Stepping 1, GenuineIntel',
        memory: {
          total: 68523712512,
          available: 38384312320,
          used: 30136610816,
          percent: 44.0
        },
        disk: {
          total: 1403713294336,
          used: 961985224704,
          free: 441728069632,
          percent: 68.5
        }
      }
    }
  } catch (error) {
    console.error('获取系统信息失败:', error)
    // 使用模拟数据
    systemInfo.value = {
      pythonVersion: '3.11.0',
      uptime: '2天 5小时 30分钟',
      mcpStatus: 'running',
      platform: 'Windows-10-10.0.26100-SP0',
      architecture: '64bit',
      processor: 'Intel64 Family 6 Model 183 Stepping 1, GenuineIntel',
      memory: {
        total: 68523712512,
        available: 38384312320,
        used: 30136610816,
        percent: 44.0
      },
      disk: {
        total: 1403713294336,
        used: 961985224704,
        free: 441728069632,
        percent: 68.5
      }
    }
  }
}

// 显示定时任务对话框
const showScheduledTasksDialog = () => {
  scheduledTasksDialogVisible.value = true
  loadScheduledTasks()
}

// 关闭定时任务对话框
const handleCloseTasksDialog = () => {
  scheduledTasksDialogVisible.value = false
}

// 加载定时任务列表
const loadScheduledTasks = async () => {
  tasksLoading.value = true
  try {
    const response = await getScheduledTasks()
    if (response.data && response.data.code === 0) {
      scheduledTasks.value = response.data.data || []
    } else {
      ElMessage.error('获取定时任务列表失败')
      scheduledTasks.value = []
    }
  } catch (error) {
    console.error('获取定时任务列表失败:', error)
    ElMessage.error('获取定时任务列表失败')
    scheduledTasks.value = []
  } finally {
    tasksLoading.value = false
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

const handleSystemInfo = () => {
  // 跳转到系统信息详情页或显示详细信息
  console.log('查看系统信息')
}

const handleServiceManagement = () => {
  // 跳转到服务管理页面
  console.log('服务管理')
}

const handleLogManagement = () => {
  // 跳转到日志管理页面
  console.log('日志管理')
}

onMounted(() => {
  loadSystemInfo()
})
</script>

<style scoped>
.system-management {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 32px;
}

.header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.header p {
  color: #666;
  font-size: 16px;
}

.management-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.management-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 16px;
}

.management-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.card-icon {
  width: 48px;
  height: 48px;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #3b82f6;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.card-content p {
  color: #666;
  font-size: 14px;
}

.card-arrow {
  color: #9ca3af;
  font-size: 18px;
}

.system-status {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
}

.system-status h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 24px;
}

.status-section {
  margin-bottom: 32px;
}

.status-section:last-child {
  margin-bottom: 0;
}

.status-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(45%, 1fr));
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.status-item.full-width {
  grid-column: 1 / -1;
}

.status-label {
  color: #666;
  font-weight: 500;
}

.status-value {
  color: #1a1a1a;
  font-weight: 600;
  text-align: right;
  word-break: break-all;
}

.status-online {
  color: #10b981 !important;
}

.resource-info {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #374151;
}

.percentage {
  color: #6b7280;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.disk {
  background: #10b981;
}

.resource-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.detail-item {
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
  color: #374151;
}

/* 图标样式 */
.icon-python::before {
  content: "🐍";
}

.icon-schedule::before {
  content: "⏰";
}

.icon-log::before {
  content: "📝";
}

.arrow-right::before {
  content: "→";
}

/* 定时任务对话框样式 */
.scheduled-tasks-container {
  padding: 8px 0;
}

.tasks-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-category-tag {
  margin-right: 8px;
}

.task-execution-time {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
}

.task-status-running {
  color: #10b981;
}

.task-status-stopped {
  color: #f59e0b;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .management-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .resource-details {
    grid-template-columns: 1fr;
  }
  
  .system-management {
    padding: 16px;
  }
}
</style> 