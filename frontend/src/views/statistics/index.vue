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
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--common-background-color);
  padding: 0;
  position: relative;
}

.ranking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
  position: relative;
  z-index: 1;
}

.statistics-container :deep(.statistics-overview),
.statistics-container :deep(.statistics-trend),
.statistics-container :deep(.ranking-dashboard),
.statistics-container :deep(.module-ranking),
.statistics-container :deep(.tool-ranking),
.statistics-container :deep(.service-ranking),
.statistics-container :deep(.tool-execution-details) {
  margin-bottom: 0 !important;
}

.statistics-container :deep(.overview-card),
.statistics-container :deep(.trend-card),
.statistics-container :deep(.dashboard-header),
.statistics-container :deep(.ranking-card),
.statistics-container :deep(.detail-card) {
  overflow: hidden;
  background: var(--common-panel-background-color) !important;
  border: 1px solid var(--common-border-color) !important;
  border-radius: var(--common-radius-lg) !important;
  box-shadow: var(--common-shadow-xs) !important;
  transform: none !important;
  backdrop-filter: none !important;
}

.statistics-container :deep(.overview-card:hover),
.statistics-container :deep(.ranking-card:hover) {
  transform: none !important;
  box-shadow: var(--common-shadow-xs) !important;
}

.statistics-container :deep(.card-header),
.statistics-container :deep(.dashboard-header) {
  min-height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0 !important;
  padding: 12px 16px !important;
  background: var(--common-panel-background-color) !important;
  border-bottom: 1px solid var(--common-border-color) !important;
}

.statistics-container :deep(.header-title),
.statistics-container :deep(.dashboard-title) {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  margin: 0 !important;
  color: var(--common-text-color-heavy) !important;
  font-size: var(--common-font-size-title-md) !important;
  font-weight: 600 !important;
  line-height: 24px !important;
}

.statistics-container :deep(.header-icon),
.statistics-container :deep(.title-icon),
.statistics-container :deep(.section-title .el-icon) {
  color: var(--common-primary-color) !important;
  font-size: 18px !important;
}

.statistics-container :deep(.refresh-button),
.statistics-container :deep(.details-button),
.statistics-container :deep(.search-append-btn) {
  border: 1px solid var(--common-primary-color) !important;
  border-radius: var(--common-radius-md) !important;
  background: var(--common-primary-color) !important;
  box-shadow: none !important;
  transform: none !important;
}

.statistics-container :deep(.refresh-button:hover),
.statistics-container :deep(.details-button:hover),
.statistics-container :deep(.search-append-btn:hover) {
  background: var(--zartd-primary-7) !important;
  transform: none !important;
}

.statistics-container :deep(.stats-grid),
.statistics-container :deep(.trend-content) {
  display: flex;
  flex-direction: column;
  gap: 16px !important;
  padding: 16px !important;
}

.statistics-container :deep(.stats-section),
.statistics-container :deep(.trend-section),
.statistics-container :deep(.trend-summary) {
  padding: 16px !important;
  background: var(--common-surface-light-color) !important;
  border: 1px solid var(--common-border-color) !important;
  border-radius: var(--common-radius-md) !important;
  box-shadow: none !important;
}

.statistics-container :deep(.section-title),
.statistics-container :deep(.summary-title) {
  min-height: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px !important;
  color: var(--common-text-color-heavy) !important;
  font-size: var(--common-font-size-base) !important;
  font-weight: 600 !important;
  line-height: 24px !important;
  text-align: left !important;
}

.statistics-container :deep(.stats-row),
.statistics-container :deep(.summary-cards) {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px !important;
}

.statistics-container :deep(.stats-section:nth-child(2) .stats-row),
.statistics-container :deep(.stats-section:nth-child(3) .stats-row) {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.statistics-container :deep(.stats-card),
.statistics-container :deep(.summary-card) {
  min-height: 76px;
  display: flex;
  align-items: center;
  padding: 12px 14px !important;
  color: var(--common-text-color) !important;
  background: var(--common-panel-background-color) !important;
  border: 1px solid var(--common-border-color) !important;
  border-radius: var(--common-radius-md) !important;
  box-shadow: none !important;
  transform: none !important;
}

.statistics-container :deep(.stats-card:hover),
.statistics-container :deep(.summary-card:hover) {
  transform: none !important;
  box-shadow: var(--common-shadow-sm) !important;
}

.statistics-container :deep(.card-content) {
  width: 100%;
  min-width: 0;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
}

.statistics-container :deep(.stats-card .card-content),
.statistics-container :deep(.summary-card .card-content) {
  height: 100%;
}

.statistics-container :deep(.card-icon) {
  width: 42px !important;
  height: 42px !important;
  flex: 0 0 42px;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  margin: 0 !important;
  color: var(--common-primary-color) !important;
  background: var(--common-primary-background-color) !important;
  border: 1px solid var(--zartd-primary-2);
  border-radius: var(--common-radius-md) !important;
  box-shadow: var(--common-shadow-xs);
  font-size: 18px !important;
}

.statistics-container :deep(.card-info),
.statistics-container :deep(.summary-card .card-content) {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.statistics-container :deep(.trend-summary .summary-card) {
  min-height: 86px;
}

.statistics-container :deep(.trend-summary .summary-card > .card-content) {
  height: auto !important;
  padding: 0 !important;
  align-items: flex-start !important;
  justify-content: center !important;
  gap: 0 !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

.statistics-container :deep(.card-value) {
  margin: 0 0 3px !important;
  color: var(--common-text-color-heavy) !important;
  font-size: 24px !important;
  font-weight: 700 !important;
  line-height: 26px !important;
  -webkit-text-fill-color: var(--common-text-color-heavy) !important;
}

.statistics-container :deep(.card-label),
.statistics-container :deep(.card-today),
.statistics-container :deep(.card-change),
.statistics-container :deep(.card-success),
.statistics-container :deep(.card-error) {
  margin: 0 !important;
  color: var(--common-text-color-light) !important;
  opacity: 1 !important;
  font-size: var(--common-font-size-secondary) !important;
  font-weight: 400 !important;
  line-height: 18px !important;
}

.statistics-container :deep(.trend-tables),
.statistics-container :deep(.ranking-dashboard .ranking-grid) {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px !important;
  margin-bottom: 16px !important;
}

.statistics-container :deep(.table-container) {
  max-height: none !important;
  overflow: auto;
}

.statistics-container :deep(.pagination-section) {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px !important;
  background: var(--common-surface-light-color) !important;
  border-top: 1px solid var(--common-border-color) !important;
}

.statistics-container :deep(.ranking-badge) {
  width: 26px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--common-radius-md);
  font-weight: 600;
  line-height: 26px;
}

.statistics-container :deep(.count-tag),
.statistics-container :deep(.group-tag),
.statistics-container :deep(.service-tag),
.statistics-container :deep(.module-tag),
.statistics-container :deep(.status-tag) {
  border-radius: var(--common-radius-sm) !important;
  background-image: none !important;
  font-weight: 500 !important;
}

.statistics-container :deep(.group-name),
.statistics-container :deep(.module-name),
.statistics-container :deep(.tool-name),
.statistics-container :deep(.service-name) {
  color: var(--common-text-color-heavy) !important;
  font-size: var(--common-font-size-base) !important;
  font-weight: 600 !important;
}

.statistics-container :deep(.creator-name),
.statistics-container :deep(.execution-time),
.statistics-container :deep(.created-time),
.statistics-container :deep(.rank-value) {
  color: var(--common-text-color) !important;
}

.statistics-container :deep(.filter-input) {
  width: 280px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .statistics-container {
    padding: 0;
  }

  .ranking-grid {
    grid-template-columns: 1fr;
  }
}
</style>
