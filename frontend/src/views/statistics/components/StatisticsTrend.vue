<template>
    <div class="statistics-trend">
        <div class="trend-card">
            <div class="card-header">
                <div class="header-title">
                    <el-icon class="header-icon">
                        <TrendCharts />
                    </el-icon>
                    统计趋势分析
                </div>
                <div class="header-controls">
                    <el-radio-group v-model="selectedPeriod" @change="onPeriodChange" class="period-selector">
                        <el-radio-button label="week">近一周</el-radio-button>
                        <el-radio-button label="month">近一月</el-radio-button>
                    </el-radio-group>
                    <el-button type="primary" size="small" @click="loadTrendData" class="refresh-button">
                        <el-icon>
                            <Refresh />
                        </el-icon>
                        刷新
                    </el-button>
                </div>
            </div>

            <div class="trend-content" v-loading="loading">
                <!-- 数据表格展示 -->
                <div class="trend-tables">
                    <!-- 左侧：MCP资源统计趋势 -->
                    <div class="trend-section">
                        <div class="section-title">
                            <el-icon>
                                <FolderOpened />
                            </el-icon>
                            MCP资源统计趋势
                        </div>
                        <el-table :data="trendData" stripe class="trend-table">
                            <el-table-column label="序号">
                                <template #default="scope">
                                    <div class="ranking-badge ranking-normal">
                                        {{ scope.$index + 1 }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column prop="statistics_date" label="日期" />
                            <el-table-column prop="total_template_groups" label="模板组" />
                            <el-table-column prop="total_templates" label="模板数" />
                            <el-table-column prop="total_services" label="服务数" />
                        </el-table>
                    </div>

                    <!-- 右侧：调用统计趋势 -->
                    <div class="trend-section">
                        <div class="section-title">
                            <el-icon>
                                <DataAnalysis />
                            </el-icon>
                            调用统计趋势
                        </div>
                        <el-table :data="trendData" stripe class="trend-table">
                            <el-table-column label="序号">
                                <template #default="scope">
                                    <div class="ranking-badge ranking-normal">
                                        {{ scope.$index + 1 }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column prop="statistics_date" label="日期" />
                            <el-table-column prop="today_new_service_calls" label="服务调用" />
                            <el-table-column prop="today_new_tools_calls" label="工具调用" />
                            <el-table-column prop="today_service_calls_success" label="服务成功" />
                            <el-table-column prop="today_service_calls_error" label="服务失败" />
                            <el-table-column prop="today_tools_calls_success" label="工具成功" />
                            <el-table-column prop="today_tools_calls_error" label="工具失败" />
                        </el-table>
                    </div>
                </div>

                <!-- 趋势汇总卡片 -->
                <div class="trend-summary" v-if="trendData.length > 0">
                    <div class="summary-title">趋势汇总 ({{ selectedPeriod === 'week' ? '近一周' : '近一月' }})</div>
                    <div class="summary-cards">
                        <div class="summary-card">
                            <div class="card-icon resource">
                                <el-icon>
                                    <FolderOpened />
                                </el-icon>
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ latestData.total_template_groups || 0 }}</div>
                                <div class="card-label">当前模板组</div>
                                <div class="card-change" :class="getChangeClass(templateGroupChange)">
                                    {{ getChangeText(templateGroupChange) }}
                                </div>
                            </div>
                        </div>

                        <div class="summary-card">
                            <div class="card-icon template">
                                <el-icon>
                                    <Document />
                                </el-icon>
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ latestData.total_templates || 0 }}</div>
                                <div class="card-label">当前模板数</div>
                                <div class="card-change" :class="getChangeClass(templateChange)">
                                    {{ getChangeText(templateChange) }}
                                </div>
                            </div>
                        </div>

                        <div class="summary-card">
                            <div class="card-icon service">
                                <el-icon>
                                    <Monitor />
                                </el-icon>
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ latestData.total_services || 0 }}</div>
                                <div class="card-label">当前服务数</div>
                                <div class="card-change" :class="getChangeClass(serviceChange)">
                                    {{ getChangeText(serviceChange) }}
                                </div>
                            </div>
                        </div>

                        <div class="summary-card">
                            <div class="card-icon call">
                                <el-icon>
                                    <Connection />
                                </el-icon>
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ totalServiceCalls }}</div>
                                <div class="card-label">总服务调用</div>
                                <div class="card-success">成功: {{ totalServiceSuccess }}</div>
                                <div class="card-error">失败: {{ totalServiceError }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
    TrendCharts,
    Refresh,
    FolderOpened,
    DataAnalysis,
    Document,
    Monitor,
    Connection
} from '@element-plus/icons-vue'
import { getStatisticsTrend } from '@/api/statistics'

// 响应式数据
const loading = ref(false)
const selectedPeriod = ref('week')
const trendData = ref([])

// 获取日期范围
const getDateRange = (period) => {
    const now = new Date()
    const endDate = now.toISOString().split('T')[0]

    let startDate
    if (period === 'week') {
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        startDate = weekAgo.toISOString().split('T')[0]
    } else {
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        startDate = monthAgo.toISOString().split('T')[0]
    }

    return { startDate, endDate }
}

// 加载趋势数据
const loadTrendData = async () => {
    loading.value = true
    try {
        const { startDate, endDate } = getDateRange(selectedPeriod.value)
        const response = await getStatisticsTrend(startDate, endDate)

        if (response && response.code === 0) {
            trendData.value = response.data || []
        }
    } catch (error) {
        console.error('获取趋势数据失败:', error)
        ElMessage.error('获取趋势数据失败')
    } finally {
        loading.value = false
    }
}

// 处理时间周期变化
const onPeriodChange = () => {
    loadTrendData()
}

// 计算属性
const latestData = computed(() => {
    return trendData.value.length > 0 ? trendData.value[trendData.value.length - 1] : {}
})

const earliestData = computed(() => {
    return trendData.value.length > 0 ? trendData.value[0] : {}
})

const templateGroupChange = computed(() => {
    if (!latestData.value.total_template_groups || !earliestData.value.total_template_groups) return 0
    return latestData.value.total_template_groups - earliestData.value.total_template_groups
})

const templateChange = computed(() => {
    if (!latestData.value.total_templates || !earliestData.value.total_templates) return 0
    return latestData.value.total_templates - earliestData.value.total_templates
})

const serviceChange = computed(() => {
    if (!latestData.value.total_services || !earliestData.value.total_services) return 0
    return latestData.value.total_services - earliestData.value.total_services
})

const totalServiceCalls = computed(() => {
    return trendData.value.reduce((sum, item) => sum + (item.today_new_service_calls || 0), 0)
})

const totalServiceSuccess = computed(() => {
    return trendData.value.reduce((sum, item) => sum + (item.today_service_calls_success || 0), 0)
})

const totalServiceError = computed(() => {
    return trendData.value.reduce((sum, item) => sum + (item.today_service_calls_error || 0), 0)
})

// 获取变化样式类
const getChangeClass = (change) => {
    if (change > 0) return 'positive'
    if (change < 0) return 'negative'
    return 'neutral'
}

// 获取变化文本
const getChangeText = (change) => {
    if (change > 0) return `+${change}`
    if (change < 0) return `${change}`
    return '无变化'
}

// 组件挂载
onMounted(() => {
    loadTrendData()
})
</script>

<style scoped>
.statistics-trend {
    margin-bottom: 32px;
}

.trend-card {
    background: var(--common-panel-background-color);
  border-radius: var(--common-radius-lg);
  box-shadow: var(--common-shadow-xs);
  border: 1px solid var(--common-border-color);
  overflow: hidden;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
  border-bottom: 1px solid var(--common-border-color);
}

.header-title {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
    color: var(--common-text-color-heavy);
}

.header-icon {
    margin-right: 8px;
    color: var(--common-primary-color);
  font-size: 18px;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 16px;
}

.period-selector {
    border-radius: 8px;
}

.refresh-button {
    border-radius: 8px;
    border-radius: var(--common-radius-md);
  border: none;
}

.trend-content {
    padding: 20px;
}

.trend-tables {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  margin-bottom: 20px;
}

.trend-section {
    background: var(--common-list-background-color);
  border-radius: var(--common-radius-lg);
  padding: 16px;
  border: 1px solid var(--common-border-color);
}

.section-title {
    display: flex;
    align-items: center;
    font-size: 16px;
    font-weight: 600;
    color: var(--common-text-color-heavy);
    margin-bottom: 12px;
}

.section-title .el-icon {
    margin-right: 8px;
    color: var(--common-primary-color);
}

.trend-table {
    font-size: 14px;
}

.trend-summary {
    background: var(--common-list-background-color);
  border-radius: var(--common-radius-lg);
  padding: 20px;
  border: 1px solid var(--common-border-color);
}

.summary-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--common-text-color-heavy);
    margin-bottom: 20px;
    text-align: center;
}

.summary-cards {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
    display: flex;
    align-items: center;
    padding: 14px;
  background: var(--common-panel-background-color);
  border-radius: var(--common-radius-md);
  border: 1px solid var(--common-border-color);
}

.card-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    font-size: 20px;
    color: var(--common-primary-color);
  background: var(--common-primary-background-color);
  border: 1px solid var(--zartd-primary-2);
}

.card-content {
    flex: 1;
}

.card-value {
    font-size: 24px;
    font-weight: bold;
    color: var(--common-text-color-heavy);
    margin-bottom: 4px;
}

.card-label {
    font-size: var(--common-font-size-base);
  color: var(--common-text-color-light);
  margin-bottom: 4px;
}

.card-change {
    font-size: 12px;
    font-weight: 500;
}

.card-change.positive {
    color: var(--common-success-color);
}

.card-change.negative {
    color: var(--common-error-color);
}

.card-change.neutral {
    color: var(--common-text-color-lighter);
}

.card-success {
    font-size: 12px;
    color: var(--common-success-color);
}

.card-error {
    font-size: 12px;
    color: var(--common-error-color);
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .trend-tables {
        grid-template-columns: 1fr;
    }

    .card-header {
        flex-direction: column;
        gap: 16px;
        align-items: flex-start;
    }

    .header-controls {
        width: 100%;
        justify-content: space-between;
    }
}

@media (max-width: 768px) {
    .statistics-trend {
        margin-bottom: 12px;
    }

    .trend-card {
        border-radius: 12px;
    }

    .card-header {
        padding: 12px;
    }

    .trend-content {
        padding: 16px 20px 20px;
    }

    .trend-section {
        padding: 16px;
    }

    .summary-cards {
        grid-template-columns: 1fr;
    }
}
</style>