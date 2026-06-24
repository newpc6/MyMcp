<template>
  <div class="system-management app-page">
    <div class="app-page-header">
      <h1 class="app-page-title">系统管理</h1>
      <p class="app-page-description">管理系统配置、Python 环境及平台运行资源</p>
    </div>

    <div class="system-layout">
      <section class="system-panel module-panel">
        <div class="panel-header">
          <div>
            <h2>功能入口</h2>
            <p>常用运维能力集中入口</p>
          </div>
        </div>

        <div class="management-grid">
          <button class="management-card" type="button" @click="$router.push('/system/python-packages')">
            <span class="card-icon">
              <el-icon><Box /></el-icon>
            </span>
            <span class="card-content">
              <strong>Python 包管理</strong>
              <em>安装、卸载和管理 Python 第三方库</em>
            </span>
            <el-icon class="card-arrow"><ArrowRight /></el-icon>
          </button>

          <button class="management-card" type="button" @click="$router.push('/system/scheduled-tasks')">
            <span class="card-icon">
              <el-icon><Timer /></el-icon>
            </span>
            <span class="card-content">
              <strong>定时任务管理</strong>
              <em>查看和管理系统定时任务</em>
            </span>
            <el-icon class="card-arrow"><ArrowRight /></el-icon>
          </button>

          <button class="management-card" type="button" @click="handleLogManagement">
            <span class="card-icon">
              <el-icon><Document /></el-icon>
            </span>
            <span class="card-content">
              <strong>日志管理</strong>
              <em>查看和管理系统运行日志</em>
            </span>
            <el-icon class="card-arrow"><ArrowRight /></el-icon>
          </button>
        </div>
      </section>

      <section class="system-panel status-panel">
        <div class="panel-header">
          <div>
            <h2>系统状态</h2>
            <p>基础运行信息与服务状态</p>
          </div>
          <el-button size="small" @click="loadSystemInfo">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-label">Python 版本</span>
            <span class="status-value">{{ systemInfo.pythonVersion }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">系统运行时间</span>
            <span class="status-value">{{ systemInfo.uptime }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">MCP 服务状态</span>
            <span class="status-value" :class="{ 'status-online': systemInfo.mcpStatus === 'running' }">
              {{ systemInfo.mcpStatus }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">操作系统</span>
            <span class="status-value">{{ systemInfo.platform }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">系统架构</span>
            <span class="status-value">{{ systemInfo.architecture }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">处理器</span>
            <span class="status-value">{{ systemInfo.processor }}</span>
          </div>
        </div>
      </section>

      <section class="system-panel resource-panel">
        <div class="panel-header">
          <div>
            <h2>资源监控</h2>
            <p>内存与磁盘使用情况</p>
          </div>
        </div>
        <div class="resource-grid">
        <div class="resource-info">
          <div class="resource-header">
              <span>内存使用情况</span>
            <span class="percentage">{{ systemInfo.memory?.percent || 0 }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: (systemInfo.memory?.percent || 0) + '%' }"></div>
          </div>
            <div class="resource-total">
              {{ formatBytes(systemInfo.memory?.used || 0) }} / {{ formatBytes(systemInfo.memory?.total || 0) }}
            </div>
          <div class="resource-details">
            <div class="detail-item">
                <span>已用</span>
                <strong>{{ formatBytes(systemInfo.memory?.used || 0) }}</strong>
            </div>
            <div class="detail-item">
                <span>可用</span>
                <strong>{{ formatBytes(systemInfo.memory?.available || 0) }}</strong>
            </div>
            <div class="detail-item">
                <span>总计</span>
                <strong>{{ formatBytes(systemInfo.memory?.total || 0) }}</strong>
            </div>
          </div>
        </div>

        <div class="resource-info">
          <div class="resource-header">
              <span>磁盘使用情况</span>
            <span class="percentage">{{ systemInfo.disk?.percent || 0 }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill disk" :style="{ width: (systemInfo.disk?.percent || 0) + '%' }"></div>
          </div>
            <div class="resource-total">
              {{ formatBytes(systemInfo.disk?.used || 0) }} / {{ formatBytes(systemInfo.disk?.total || 0) }}
            </div>
          <div class="resource-details">
            <div class="detail-item">
                <span>已用</span>
                <strong>{{ formatBytes(systemInfo.disk?.used || 0) }}</strong>
            </div>
            <div class="detail-item">
                <span>可用</span>
                <strong>{{ formatBytes(systemInfo.disk?.free || 0) }}</strong>
            </div>
            <div class="detail-item">
                <span>总计</span>
                <strong>{{ formatBytes(systemInfo.disk?.total || 0) }}</strong>
            </div>
          </div>
        </div>
      </div>
      </section>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, Box, Document, Refresh, Timer } from '@element-plus/icons-vue'
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
  color: var(--common-text-color);
}

.system-layout {
  display: grid;
  grid-template-columns: minmax(360px, 420px) minmax(0, 1fr);
  gap: 8px;
  align-items: start;
}

.system-panel {
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-md);
  box-shadow: var(--common-shadow-sm);
}

.module-panel {
  grid-row: span 2;
}

.panel-header {
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--common-border-color);
}

.panel-header h2 {
  margin: 0;
  color: var(--common-text-color-heavy);
  font-size: 14px;
  font-weight: 600;
  line-height: 22px;
}

.panel-header p {
  margin: 2px 0 0;
  color: var(--common-text-color-light);
  font-size: 12px;
  line-height: 18px;
}

.management-grid {
  display: grid;
  gap: 8px;
  padding: 8px;
}

.management-card {
  width: 100%;
  min-height: 72px;
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) 18px;
  gap: 12px;
  align-items: center;
  padding: 12px;
  color: var(--common-text-color);
  text-align: left;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-md);
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.management-card:hover {
  background: var(--common-hover-background-color);
  border-color: var(--common-primary-color);
  box-shadow: var(--common-shadow-sm);
}

.card-icon {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--common-primary-color);
  background: var(--common-primary-background-color);
  border-radius: var(--common-radius-md);
  font-size: 20px;
}

.card-content {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.card-content strong {
  color: var(--common-text-color-heavy);
  font-size: 14px;
  font-weight: 600;
  line-height: 22px;
}

.card-content em {
  margin-top: 2px;
  overflow: hidden;
  color: var(--common-text-color-light);
  font-size: 12px;
  font-style: normal;
  line-height: 18px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-arrow {
  color: var(--common-text-color-lighter);
  font-size: 16px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  padding: 8px;
  background: var(--common-border-color);
}

.status-item {
  min-height: 48px;
  display: grid;
  grid-template-columns: 128px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  padding: 8px 12px;
  background: var(--common-panel-background-color);
}

.status-label {
  color: var(--common-text-color-light);
  font-size: 12px;
  line-height: 20px;
}

.status-value {
  min-width: 0;
  overflow: hidden;
  color: var(--common-text-color-heavy);
  font-size: 13px;
  font-weight: 600;
  line-height: 20px;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-online {
  color: var(--common-success-color) !important;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 8px;
}

.resource-info {
  padding: 16px;
  background: var(--common-hover-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-md);
}

.resource-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  color: var(--common-text-color-heavy);
  font-size: 14px;
  font-weight: 600;
  line-height: 22px;
}

.percentage {
  color: var(--common-primary-color);
  font-size: 18px;
  font-weight: 600;
  line-height: 24px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  overflow: hidden;
  background: var(--common-border-color);
  border-radius: var(--common-radius-sm);
}

.progress-fill {
  height: 100%;
  background: var(--common-primary-color);
  border-radius: var(--common-radius-sm);
  transition: width 0.3s ease;
}

.progress-fill.disk {
  background: var(--common-success-color);
}

.resource-total {
  margin-top: 8px;
  color: var(--common-text-color-light);
  font-size: 12px;
  line-height: 20px;
}

.resource-details {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.detail-item {
  min-width: 0;
  padding: 8px;
  background: var(--common-panel-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-sm);
}

.detail-item span,
.detail-item strong {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-item span {
  color: var(--common-text-color-light);
  font-size: 12px;
  line-height: 18px;
}

.detail-item strong {
  margin-top: 2px;
  color: var(--common-text-color-heavy);
  font-size: 13px;
  font-weight: 600;
  line-height: 20px;
}

.scheduled-tasks-container {
  padding: 8px 0;
}

.tasks-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.task-category-tag {
  margin-right: 8px;
}

.task-execution-time {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
}

.task-status-running {
  color: var(--common-success-color);
}

.task-status-stopped {
  color: var(--common-warning-color);
}
</style>
