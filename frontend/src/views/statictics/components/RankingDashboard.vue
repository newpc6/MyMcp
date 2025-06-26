<template>
    <div class="ranking-dashboard">
        <!-- 标题和控制区域 -->
        <div class="dashboard-header">
            <h2 class="dashboard-title">
                <el-icon class="title-icon">
                    <TrendCharts />
                </el-icon>
                排行榜仪表板
            </h2>
            <div class="control-section">
                <el-select v-model="selectedLimit" @change="handleLimitChange" size="default" style="width: 120px;">
                    <el-option label="前五名" :value="5" />
                    <el-option label="前十名" :value="10" />
                </el-select>
                <el-button type="primary" @click="refreshAll" :loading="refreshing">
                    <el-icon>
                        <Refresh />
                    </el-icon>
                    刷新数据
                </el-button>
            </div>
        </div>

        <!-- 排行榜网格 -->
        <div class="ranking-grid">
            <!-- MCP分组排行榜 -->
            <div class="ranking-card">
                <div class="card-header">
                    <div class="header-title">
                        <el-icon class="header-icon">
                            <FolderOpened />
                        </el-icon>
                        MCP分组排行榜
                    </div>
                    <div class="ranking-type-selector">
                        <el-radio-group v-model="groupOrderBy" @change="loadGroupRankings" size="small">
                            <el-radio-button value="templates_count">模板数量</el-radio-button>
                            <el-radio-button value="services_count">发布服务</el-radio-button>
                            <el-radio-button value="call_count">服务调用</el-radio-button>
                        </el-radio-group>
                    </div>
                </div>

                <div class="table-container">
                    <el-table :data="groupRankings" stripe v-loading="loadingGroups" class="ranking-table"
                        :header-cell-style="{ background: '#f8fafc', color: '#4a5568', fontWeight: '600' }">
                        <el-table-column label="排名" width="60" align="center">
                            <template #default="scope">
                                <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                                    {{ scope.$index + 1 }}
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column prop="group_name" label="分组名称" min-width="140">
                            <template #default="scope">
                                <div class="group-info">
                                    <span class="group-name">{{ scope.row.group_name }}</span>
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column label="模板数" align="center">
                            <template #default="scope">
                                <el-tag size="small" type="primary" effect="light" class="count-tag">
                                    {{ scope.row.templates_count }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="服务数" align="center">
                            <template #default="scope">
                                <el-tag size="small" type="success" effect="light" class="count-tag">
                                    {{ scope.row.services_count }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="调用次数" align="center">
                            <template #default="scope">
                                <el-tag size="small" type="warning" effect="light" class="count-tag">
                                    {{ scope.row.call_count }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="排序值" align="center">
                            <template #default="scope">
                                <span class="rank-value">{{ getRankValue(scope.row) }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </div>

            <!-- MCP模板排行榜 -->
            <div class="ranking-card">
                <div class="card-header">
                    <div class="header-title">
                        <el-icon class="header-icon">
                            <Document />
                        </el-icon>
                        MCP模板排行榜
                    </div>
                    <div class="ranking-type-selector">
                        <el-radio-group v-model="moduleOrderBy" @change="loadModuleRankings" size="small">
                            <el-radio-button value="services_count">发布服务</el-radio-button>
                            <el-radio-button value="call_count">服务调用</el-radio-button>
                        </el-radio-group>
                    </div>
                </div>

                <div class="table-container">
                    <el-table :data="moduleRankings" stripe v-loading="loadingModules" class="ranking-table"
                        :header-cell-style="{ background: '#f8fafc', color: '#4a5568', fontWeight: '600' }">
                        <el-table-column label="排名" width="60" align="center">
                            <template #default="scope">
                                <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                                    {{ scope.$index + 1 }}
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column label="模板名称" min-width="140">
                            <template #default="scope">
                                <div class="module-info">
                                    <div class="module-name">{{ scope.row.name }}</div>
                                    <div class="module-description">{{ scope.row.description || '暂无描述' }}</div>
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column label="分组" align="center">
                            <template #default="scope">
                                <el-tag size="small" effect="plain" class="group-tag">
                                    {{ scope.row.category_name }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="服务数" align="center">
                            <template #default="scope">
                                <el-tag size="small" type="success" effect="light" class="count-tag">
                                    {{ scope.row.services_count }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="调用次数" align="center">
                            <template #default="scope">
                                <el-tag size="small" type="warning" effect="light" class="count-tag">
                                    {{ scope.row.call_count }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="排序值" align="center">
                            <template #default="scope">
                                <span class="rank-value">{{ getModuleRankValue(scope.row) }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
    TrendCharts,
    Refresh,
    FolderOpened,
    Document
} from '@element-plus/icons-vue'
import {
    getGroupStatsRanking,
    getModuleStatsRanking
} from '@/api/statistics'
import { getRankingClass } from '@/utils/table'
// 响应式数据
const selectedLimit = ref(10)
const refreshing = ref(false)

// 分组排行榜数据
const groupRankings = ref([])
const loadingGroups = ref(false)
const groupOrderBy = ref('services_count')

// 模板排行榜数据
const moduleRankings = ref([])
const loadingModules = ref(false)
const moduleOrderBy = ref('services_count')

// 获取分组排序值
const getRankValue = (row) => {
    switch (groupOrderBy.value) {
        case 'templates_count':
            return row.templates_count
        case 'services_count':
            return row.services_count
        case 'call_count':
            return row.call_count
        default:
            return row.services_count
    }
}

// 获取模板排序值
const getModuleRankValue = (row) => {
    switch (moduleOrderBy.value) {
        case 'services_count':
            return row.services_count
        case 'call_count':
            return row.call_count
        default:
            return row.services_count
    }
}

// 加载分组排行榜
const loadGroupRankings = async () => {
    loadingGroups.value = true
    try {
        const response = await getGroupStatsRanking(
            groupOrderBy.value,
            selectedLimit.value,
            true
        )
        if (response && response.code === 0) {
            groupRankings.value = response.data || []
        } else {
            ElMessage.error(response?.message || '获取分组排行榜失败')
        }
    } catch (error) {
        console.error('获取分组排行榜失败:', error)
        ElMessage.error('获取分组排行榜失败')
    } finally {
        loadingGroups.value = false
    }
}

// 加载模板排行榜
const loadModuleRankings = async () => {
    loadingModules.value = true
    try {
        const response = await getModuleStatsRanking(
            moduleOrderBy.value,
            selectedLimit.value,
            true
        )
        if (response && response.code === 0) {
            moduleRankings.value = response.data || []
        } else {
            ElMessage.error(response?.message || '获取模板排行榜失败')
        }
    } catch (error) {
        console.error('获取模板排行榜失败:', error)
        ElMessage.error('获取模板排行榜失败')
    } finally {
        loadingModules.value = false
    }
}

// 处理数量限制变化
const handleLimitChange = () => {
    loadGroupRankings()
    loadModuleRankings()
}

// 刷新所有数据
const refreshAll = async () => {
    refreshing.value = true
    try {
        await Promise.all([
            loadGroupRankings(),
            loadModuleRankings()
        ])
        ElMessage.success('数据刷新成功')
    } catch (error) {
        ElMessage.error('数据刷新失败')
    } finally {
        refreshing.value = false
    }
}

// 组件挂载时加载数据
onMounted(() => {
    loadGroupRankings()
    loadModuleRankings()
})
</script>

<style scoped>
.ranking-dashboard {
    /* padding: 24px; */
    /* background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
    min-height: calc(100vh - 120px);
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 20px 24px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.dashboard-title {
    font-size: 24px;
    font-weight: 700;
    color: #1565c0;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.title-icon {
    font-size: 28px;
    color: #2196f3;
}

.control-section {
    display: flex;
    align-items: center;
    gap: 16px;
}

.ranking-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    height: calc(100vh - 240px);
}

.ranking-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
}

.ranking-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.card-header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid rgba(21, 101, 192, 0.1);
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.05) 0%, rgba(25, 118, 210, 0.05) 100%);
}

.header-title {
    font-size: 18px;
    font-weight: 700;
    color: #1565c0;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.header-icon {
    font-size: 20px;
    color: #2196f3;
}

.ranking-type-selector {
    display: flex;
    justify-content: center;
}

.table-container {
    flex: 1;
    overflow-y: auto;
    max-height: calc(100vh - 360px);
}

.ranking-table {
    border-radius: 0;
}

.ranking-table :deep(.el-table__row:hover) {
    background-color: rgba(33, 150, 243, 0.05) !important;
}

.ranking-table :deep(.el-table__row--striped) {
    background-color: rgba(248, 250, 252, 0.8);
}

.group-info,
.module-info {
    text-align: left;
}

.group-name,
.module-name {
    font-weight: 600;
    color: #2c3e50;
    font-size: 14px;
}

.module-description {
    font-size: 12px;
    color: #7f8c8d;
    margin-top: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 200px;
}

.count-tag {
    font-weight: 600;
    border-radius: 12px;
}

.group-tag {
    font-size: 11px;
    border-radius: 8px;
}

.rank-value {
    font-weight: 700;
    color: #e91e63;
    font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .ranking-grid {
        grid-template-columns: 1fr;
        gap: 16px;
    }

    .dashboard-header {
        flex-direction: column;
        gap: 16px;
        align-items: stretch;
    }

    .control-section {
        justify-content: center;
    }
}
</style>