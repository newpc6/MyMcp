<template>
  <div class="statistics-container">
    <!-- 统计概览 - 合并的卡片 -->
    <StatisticsOverview 
      :service-stats="serviceStats" 
      @refresh="refreshAllStatistics" 
    />

    <!-- 统计趋势分析 -->
    <StatisticsTrend />

    <!-- 排行榜仪表板 -->
    <RankingDashboard />

    <!-- 排名网格 -->
    <div class="ranking-grid">
      <!-- 模块发布排名 -->
      <ModuleRanking
        :module-rankings="moduleRankings"
        :loading="loadingModules"
        :current-page="moduleCurrentPage"
        :page-size="modulePageSize"
        :total-items="moduleTotalItems"
        @refresh="refreshModuleRankings"
        @size-change="handleModuleSizeChange"
        @page-change="handleModulePageChange"
      />

      <!-- 工具调用排名 -->
      <ToolRanking
        :tool-rankings="toolRankings"
        :loading="loadingTools"
        :current-page="toolCurrentPage"
        :page-size="toolPageSize"
        :total-items="toolTotalItems"
        @refresh="refreshToolRankings"
        @size-change="handleToolSizeChange"
        @page-change="handleToolPageChange"
      />

      <!-- 服务调用排名 -->
      <ServiceRanking
        :service-rankings="serviceRankings"
        :loading="loadingServices"
        :current-page="serviceCurrentPage"
        :page-size="servicePageSize"
        :total-items="serviceTotalItems"
        @refresh="refreshServiceRankings"
        @size-change="handleServiceSizeChange"
        @page-change="handleServicePageChange"
      />
    </div>

    <!-- 工具调用详情 -->
    <ToolExecutionDetails
      :tool-executions="toolExecutions"
      :loading="loadingExecutions"
      :current-page="currentPage"
      :page-size="pageSize"
      @search="handleToolSearch"
      @size-change="handleSizeChange"
      @page-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import StatisticsOverview from './components/StatisticsOverview.vue'
import ModuleRanking from './components/ModuleRanking.vue'
import ToolRanking from './components/ToolRanking.vue'
import ServiceRanking from './components/ServiceRanking.vue'
import ToolExecutionDetails from './components/ToolExecutionDetails.vue'
import StatisticsTrend from './components/StatisticsTrend.vue'
import RankingDashboard from './components/RankingDashboard.vue'
import {
  getServiceStats,
  getModuleRankings,
  getToolRankings,
  getServiceRankings,
  getToolExecutions,
  refreshStatistics
} from '@/api/statistics'

// 统计数据
const serviceStats = ref({
  total_services: 0,
  running_services: 0,
  stopped_services: 0,
  error_services: 0,
  total_template_groups: 0,
  today_new_template_groups: 0,
  total_templates: 0,
  today_new_templates: 0,
  total_service_calls: 0,
  today_new_service_calls: 0,
  total_tools_calls: 0,
  today_new_tools_calls: 0
})

// 模块排名数据
const moduleRankings = ref([])
const loadingModules = ref(false)
const moduleCurrentPage = ref(1)
const modulePageSize = ref(5)
const moduleTotalItems = ref(0)

// 工具排名数据
const toolRankings = ref([])
const loadingTools = ref(false)
const toolCurrentPage = ref(1)
const toolPageSize = ref(5)
const toolTotalItems = ref(0)

// 服务排名数据
const serviceRankings = ref([])
const loadingServices = ref(false)
const serviceCurrentPage = ref(1)
const servicePageSize = ref(5)
const serviceTotalItems = ref(0)

// 工具调用详情数据
const toolExecutions = ref({
  items: [],
  total: 0,
  page: 1
})
const loadingExecutions = ref(false)
const currentPage = ref(1)
const pageSize = ref(5)

// 获取服务统计数据
const loadServiceStats = async () => {
  try {
    const response = await getServiceStats()
    if (response && response.code === 0) {
      serviceStats.value = response.data
    }
  } catch (error) {
    console.error('获取服务统计数据失败', error)
    ElMessage.error('获取服务统计数据失败')
  }
}

// 获取模块发布排名
const loadModuleRankings = async (page = 1) => {
  loadingModules.value = true
  try {
    const response = await getModuleRankings(modulePageSize.value, page)
    if (response && response.code === 0) {
      moduleRankings.value = response.data.items
      moduleTotalItems.value = response.data.total
      moduleCurrentPage.value = response.data.page || page
    }
  } catch (error) {
    console.error('获取模块排名失败', error)
    ElMessage.error('获取模块排名失败')
  } finally {
    loadingModules.value = false
  }
}

// 获取工具调用排名
const loadToolRankings = async (page = 1) => {
  loadingTools.value = true
  try {
    const response = await getToolRankings(toolPageSize.value, page)
    if (response && response.code === 0) {
      toolRankings.value = response.data.items
      toolTotalItems.value = response.data.total
      toolCurrentPage.value = response.data.page || page
    }
  } catch (error) {
    console.error('获取工具排名失败', error)
    ElMessage.error('获取工具排名失败')
  } finally {
    loadingTools.value = false
  }
}

// 获取服务调用排名
const loadServiceRankings = async (page = 1) => {
  loadingServices.value = true
  try {
    const response = await getServiceRankings(servicePageSize.value, page)
    if (response && response.code === 0) {
      serviceRankings.value = response.data.items
      serviceTotalItems.value = response.data.total
      serviceCurrentPage.value = response.data.page || page
    }
  } catch (error) {
    console.error('获取服务排名失败', error)
    ElMessage.error('获取服务排名失败')
  } finally {
    loadingServices.value = false
  }
}

// 获取工具调用详情
const loadToolExecutions = async (page, filter = '') => {
  if (page) currentPage.value = page
  loadingExecutions.value = true

  try {
    const response = await getToolExecutions(
      currentPage.value,
      pageSize.value,
      filter || undefined
    )

    if (response && response.code === 0) {
      toolExecutions.value = response.data
      currentPage.value = response.data.page || currentPage.value
    }
  } catch (error) {
    console.error('获取工具调用详情失败', error)
    ElMessage.error('获取工具调用详情失败')
  } finally {
    loadingExecutions.value = false
  }
}

// 刷新统计数据
const refreshAllStatistics = async () => {
  try {
    const response = await refreshStatistics()
    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: '统计数据已刷新',
        type: 'success'
      })

      // 重新加载所有数据
      loadServiceStats()
      refreshModuleRankings()
      refreshToolRankings()
      refreshServiceRankings()
      loadToolExecutions()
    }
  } catch (error) {
    console.error('刷新统计数据失败', error)
    ElMessage.error('刷新统计数据失败')
  }
}

// 模块排名分页处理函数
const handleModulePageChange = (page) => {
  moduleCurrentPage.value = page
  loadModuleRankings(page)
}

const handleModuleSizeChange = (size) => {
  modulePageSize.value = size
  moduleCurrentPage.value = 1
  loadModuleRankings(1)
}

// 工具排名分页处理函数
const handleToolPageChange = (page) => {
  toolCurrentPage.value = page
  loadToolRankings(page)
}

const handleToolSizeChange = (size) => {
  toolPageSize.value = size
  toolCurrentPage.value = 1
  loadToolRankings(1)
}

// 服务排名分页处理函数
const handleServicePageChange = (page) => {
  serviceCurrentPage.value = page
  loadServiceRankings(page)
}

const handleServiceSizeChange = (size) => {
  servicePageSize.value = size
  serviceCurrentPage.value = 1
  loadServiceRankings(1)
}

// 刷新模块排名
const refreshModuleRankings = () => {
  moduleCurrentPage.value = 1
  loadModuleRankings(1)
}

// 刷新工具排名
const refreshToolRankings = () => {
  toolCurrentPage.value = 1
  loadToolRankings(1)
}

// 刷新服务排名
const refreshServiceRankings = () => {
  serviceCurrentPage.value = 1
  loadServiceRankings(1)
}

// 工具调用详情分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadToolExecutions(1)
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadToolExecutions(page)
}

// 工具搜索处理
const handleToolSearch = (filter) => {
  currentPage.value = 1
  loadToolExecutions(1, filter)
}

// 组件挂载时加载数据
onMounted(() => {
  loadServiceStats()
  loadModuleRankings()
  loadToolRankings()
  loadServiceRankings()
  loadToolExecutions()
})
</script>

<style scoped>
.statistics-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0efff 0%, #d1d1d1 100%);
  padding: 32px;
  position: relative;
  overflow: hidden;
}

.statistics-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  pointer-events: none;
}

.ranking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .statistics-container {
    padding: 16px;
  }

  .ranking-grid {
    grid-template-columns: 1fr;
  }
}
</style>