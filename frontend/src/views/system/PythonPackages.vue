<template>
  <div class="python-packages">
    <div class="header">
      <div class="header-top">
        <button @click="goBack" class="back-btn">
          ← 返回
        </button>
        <div class="header-content">
          <h1>Python包管理</h1>
          <p>管理Python第三方库的安装、升级和卸载</p>  
        </div>
      </div>
    </div>

    <!-- 安装新包 -->
    <div class="install-section">
      <div class="section-header">
        <h2>安装新包</h2>
      </div>
      <div class="install-form">
        <div class="form-row">
          <input
            v-model="packageToInstall"
            type="text"
            placeholder="输入包名，例如: requests, numpy==1.21.0"
            class="package-input"
            @keyup.enter="installPackage"
          />
          <button 
            @click="installPackage" 
            :disabled="installing || !packageToInstall.trim()"
            class="install-btn"
          >
            {{ installing ? '安装中...' : '安装' }}
          </button>
        </div>
        <div class="install-options">
          <label class="checkbox-label">
            <input type="checkbox" v-model="upgradeIfExists" />
            如果已存在则升级
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="useUserInstall" />
            用户级安装 (--user)
          </label>
        </div>
        <div class="mirror-settings">
          <label class="mirror-label">镜像源设置:</label>
          <select v-model="selectedMirror" class="mirror-select">
            <option value="https://pypi.tuna.tsinghua.edu.cn/simple/">清华大学镜像:https://pypi.tuna.tsinghua.edu.cn/simple/</option>
            <option value="https://mirrors.aliyun.com/pypi/simple/">阿里云镜像:https://mirrors.aliyun.com/pypi/simple/</option>
            <option value="https://pypi.douban.com/simple/">豆瓣镜像:https://pypi.douban.com/simple/</option>
            <option value="https://pypi.mirrors.ustc.edu.cn/simple/">中科大镜像:https://pypi.mirrors.ustc.edu.cn/simple/</option>
            <option value="https://pypi.org/simple/">官方源:https://pypi.org/simple/</option>
            <option value="custom">自定义</option>
          </select>
          <input
            v-if="selectedMirror === 'custom'"
            v-model="customMirror"
            type="text"
            placeholder="输入自定义镜像源URL"
            class="custom-mirror-input"
          />
        </div>
      </div>
    </div>

    <!-- 已安装包列表 -->
    <div class="packages-section">
      <div class="section-header">
        <h2>已安装包 ({{ filteredPackages.length }})</h2>
        <div class="header-actions">
          <input
            v-model="searchTerm"
            type="text"
            placeholder="搜索包..."
            class="search-input"
          />
          <button @click="refreshPackages" :disabled="loading" class="refresh-btn">
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
        </div>
      </div>

      <div class="packages-list" v-if="!loading">
        <div 
          v-for="pkg in paginatedPackages" 
          :key="pkg.name"
          class="package-item"
        >
          <div class="package-info">
            <div class="package-name">{{ pkg.name }}</div>
            <div class="package-version">v{{ pkg.version }}</div>
            <div class="package-summary" v-if="pkg.summary">{{ pkg.summary }}</div>
          </div>
          <div class="package-actions">
            <button 
              @click="upgradePackage(pkg.name)"
              :disabled="upgrading.includes(pkg.name)"
              class="action-btn upgrade-btn"
            >
              {{ upgrading.includes(pkg.name) ? '升级中...' : '升级' }}
            </button>
            <button 
              @click="uninstallPackage(pkg.name)"
              :disabled="uninstalling.includes(pkg.name)"
              class="action-btn uninstall-btn"
            >
              {{ uninstalling.includes(pkg.name) ? '卸载中...' : '卸载' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载包列表中...</p>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="page-btn"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 操作日志 -->
    <div class="logs-section" v-if="operationLogs.length > 0">
      <div class="section-header">
        <h2>操作日志</h2>
        <button @click="clearLogs" class="clear-btn">清空日志</button>
      </div>
      <div class="logs-container">
        <div 
          v-for="log in operationLogs" 
          :key="log.id"
          class="log-item"
          :class="log.type"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getInstalledPackages, installPackage as apiInstallPackage, upgradePackage as apiUpgradePackage, uninstallPackage as apiUninstallPackage } from '../../api/system'

interface Package {
  name: string
  version: string
  summary?: string
}

interface OperationLog {
  id: number
  timestamp: Date
  type: 'success' | 'error' | 'info'
  message: string
}

const router = useRouter()
const packageToInstall = ref('')
const upgradeIfExists = ref(false)
const useUserInstall = ref(false)
const installing = ref(false)

// 镜像源相关
const selectedMirror = ref('https://pypi.tuna.tsinghua.edu.cn/simple/')
const customMirror = ref('')

const packages = ref<Package[]>([])
const loading = ref(false)
const searchTerm = ref('')
const currentPage = ref(1)
const pageSize = 20

const upgrading = ref<string[]>([])
const uninstalling = ref<string[]>([])

const operationLogs = ref<OperationLog[]>([])
let logIdCounter = 0

// 计算当前使用的镜像源
const currentMirror = computed(() => {
  return selectedMirror.value === 'custom' ? customMirror.value : selectedMirror.value
})

const filteredPackages = computed(() => {
  if (!searchTerm.value) return packages.value
  const term = searchTerm.value.toLowerCase()
  return packages.value.filter(pkg => 
    pkg.name.toLowerCase().includes(term) ||
    (pkg.summary && pkg.summary.toLowerCase().includes(term))
  )
})

const totalPages = computed(() => 
  Math.ceil(filteredPackages.value.length / pageSize)
)

const paginatedPackages = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredPackages.value.slice(start, end)
})

const goBack = () => {
  router.back()
}

const addLog = (type: 'success' | 'error' | 'info', message: string) => {
  operationLogs.value.unshift({
    id: ++logIdCounter,
    timestamp: new Date(),
    type,
    message
  })
  
  // 限制日志数量
  if (operationLogs.value.length > 100) {
    operationLogs.value = operationLogs.value.slice(0, 100)
  }
}

const loadPackages = async () => {
  loading.value = true
  try {
    // 调用后端API获取已安装包列表
    const response = await getInstalledPackages()
    
    // 检查响应格式并正确提取数据
    if (response.data && response.data.code === 0) {
      packages.value = response.data.data || []
    } else if (Array.isArray(response.data)) {
      packages.value = response.data
    } else {
      packages.value = []
      console.warn('API返回的数据格式不正确:', response.data)
    }
    
    addLog('info', `加载了 ${packages.value.length} 个已安装的包`)
  } catch (error) {
    console.error('加载包列表失败:', error)
    addLog('error', '加载包列表失败: ' + error)
    packages.value = [] // 确保packages.value始终是数组
  } finally {
    loading.value = false
  }
}

const installPackage = async () => {
  if (!packageToInstall.value.trim()) return
  
  installing.value = true
  const packageName = packageToInstall.value.trim()
  
  try {
    addLog('info', `开始安装包: ${packageName} (使用镜像源: ${currentMirror.value})`)
    
    // 调用后端API安装包
    const response = await apiInstallPackage({
      package: packageName,
      upgrade: upgradeIfExists.value,
      user: useUserInstall.value,
      index_url: currentMirror.value
    })
    
    // 检查响应状态
    if (response.data && response.data.code === 0) {
      addLog('success', `成功安装包: ${packageName}`)
      packageToInstall.value = ''
      
      // 刷新包列表
      await loadPackages()
    } else {
      throw new Error(response.data?.message || '安装失败')
    }
  } catch (error) {
    console.error('安装包失败:', error)
    addLog('error', `安装包失败: ${packageName} - ${error}`)
  } finally {
    installing.value = false
  }
}

const upgradePackage = async (packageName: string) => {
  upgrading.value.push(packageName)
  
  try {
    addLog('info', `开始升级包: ${packageName} (使用镜像源: ${currentMirror.value})`)
    
    // 调用后端API升级包
    const response = await apiUpgradePackage({
      package: packageName,
      index_url: currentMirror.value
    })
    
    // 检查响应状态
    if (response.data && response.data.code === 0) {
      addLog('success', `成功升级包: ${packageName}`)
      
      // 刷新包列表
      await loadPackages()
    } else {
      throw new Error(response.data?.message || '升级失败')
    }
  } catch (error) {
    console.error('升级包失败:', error)
    addLog('error', `升级包失败: ${packageName} - ${error}`)
  } finally {
    upgrading.value = upgrading.value.filter(name => name !== packageName)
  }
}

const uninstallPackage = async (packageName: string) => {
  if (!confirm(`确定要卸载包 "${packageName}" 吗？`)) return
  
  uninstalling.value.push(packageName)
  
  try {
    addLog('info', `开始卸载包: ${packageName}`)
    
    // 调用后端API卸载包
    const response = await apiUninstallPackage(packageName)
    
    // 检查响应状态
    if (response.data && response.data.code === 0) {
      addLog('success', `成功卸载包: ${packageName}`)
      
      // 从列表中移除
      packages.value = packages.value.filter(pkg => pkg.name !== packageName)
    } else {
      throw new Error(response.data?.message || '卸载失败')
    }
  } catch (error) {
    console.error('卸载包失败:', error)
    addLog('error', `卸载包失败: ${packageName} - ${error}`)
  } finally {
    uninstalling.value = uninstalling.value.filter(name => name !== packageName)
  }
}

const refreshPackages = () => {
  loadPackages()
}

const clearLogs = () => {
  operationLogs.value = []
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN')
}

onMounted(() => {
  loadPackages()
})
</script>

<style scoped>
.python-packages {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 32px;
}

.header-top {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.back-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.back-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.header-content {
  flex: 1;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.header-content p {
  color: #666;
  font-size: 16px;
}

.install-section,
.packages-section,
.logs-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.package-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.package-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.install-btn {
  padding: 12px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.install-btn:hover:not(:disabled) {
  background: #2563eb;
}

.install-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.install-options {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
}

.mirror-settings {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.mirror-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.mirror-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  min-width: 150px;
}

.mirror-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.custom-mirror-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-width: 300px;
}

.custom-mirror-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  width: 200px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.packages-list {
  space-y: 12px;
}

.package-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 12px;
}

.package-info {
  flex: 1;
}

.package-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.package-version {
  font-size: 14px;
  color: #3b82f6;
  margin-top: 2px;
}

.package-summary {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.package-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.upgrade-btn {
  background: #f0f9ff;
  border-color: #3b82f6;
  color: #3b82f6;
}

.upgrade-btn:hover:not(:disabled) {
  background: #3b82f6;
  color: white;
}

.uninstall-btn {
  background: #fef2f2;
  border-color: #ef4444;
  color: #ef4444;
}

.uninstall-btn:hover:not(:disabled) {
  background: #ef4444;
  color: white;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #666;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.page-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  font-size: 14px;
  border-bottom: 1px solid #f3f4f6;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.success {
  background: #f0fdf4;
  color: #166534;
}

.log-item.error {
  background: #fef2f2;
  color: #dc2626;
}

.log-item.info {
  background: #f0f9ff;
  color: #1e40af;
}

.log-time {
  font-size: 12px;
  color: #666;
  min-width: 80px;
}

.clear-btn {
  padding: 6px 12px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.clear-btn:hover {
  background: #e5e7eb;
}
</style> 