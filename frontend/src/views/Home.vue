<template>
    <div class="home-container">
        <!-- 顶部卡片统计区域 -->
        <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
                <el-card class="statistic-card" shadow="hover">
                    <div class="flex">
                        <div class="icon-container module-icon">
                            <el-icon>
                                <Suitcase />
                            </el-icon>
                        </div>
                        <div class="statistic-content">
                            <div class="statistic-title">模块总数</div>
                            <div class="statistic-value">{{ moduleCount }}</div>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <el-col :xs="24" :sm="12" :md="6">
                <el-card class="statistic-card" shadow="hover">
                    <div class="flex">
                        <div class="icon-container tool-icon">
                            <el-icon>
                                <Tools />
                            </el-icon>
                        </div>
                        <div class="statistic-content">
                            <div class="statistic-title">工具总数</div>
                            <div class="statistic-value">{{ toolCount }}</div>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <el-col :xs="24" :sm="12" :md="6">
                <el-card class="statistic-card" shadow="hover" v-loading="loading.stats">
                    <div class="flex">

                        <div class="icon-container run-icon">
                            <el-icon>
                                <DataAnalysis />
                            </el-icon>
                        </div>
                        <div class="statistic-content">
                            <div class="statistic-title">执行次数</div>
                            <div class="statistic-value">{{ executionCount }}</div>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <el-col :xs="24" :sm="12" :md="6">
                <el-card class="statistic-card" shadow="hover" v-loading="loading.stats">
                    <div class="flex">
                        <div class="icon-container update-icon">
                            <el-icon>
                                <Timer />
                            </el-icon>
                        </div>
                        <div class="statistic-content">
                            <div class="statistic-title">最近更新</div>
                            <div class="statistic-value">{{ lastUpdateTime }}</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 工具快捷区 -->
        <el-row :gutter="20" class="mt-20">
            <el-col :span="24">
                <el-card shadow="hover">
                    <template #header>
                        <div class="card-header tech-header">
                            <span>常用工具</span>
                        </div>
                    </template>

                    <div class="tool-grid">
                        <el-card v-for="tool in favoriteTools" :key="tool.name" class="tool-card" shadow="hover"
                            @click="goToTool(tool.name)">
                            <div class="tool-card-content">
                                <el-icon>
                                    <Connection />
                                </el-icon>
                                <h3>{{ tool.name }}</h3>
                                <p>{{ truncateText(tool.doc, 60) }}</p>
                            </div>
                        </el-card>

                        <el-card v-if="favoriteTools.length < 6" class="tool-card add-tool" shadow="hover"
                            @click="router.push({ name: 'Tools' })">
                            <div class="tool-card-content">
                                <el-icon>
                                    <Plus />
                                </el-icon>
                                <h3>添加工具</h3>
                            </div>
                        </el-card>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 工具调用记录 -->
        <el-row :gutter="20" class="mt-15">
            <el-col :span="24">
                <el-card shadow="hover" v-loading="loading.executions">
                    <template #header>
                        <div class="card-header tech-header">
                            <span>工具调用记录</span>
                        </div>
                        <div class="flex-end">
                            <el-input v-model="searchQuery" placeholder="搜索工具..." class="search-input" clearable>
                                <template #prefix>
                                    <el-icon>
                                        <Search />
                                    </el-icon>
                                </template>
                            </el-input>
                            <el-button type="primary" class="search-button" @click="fetchRecentExecutions">
                                刷新
                                <el-icon class="ml-5">
                                    <Refresh />
                                </el-icon>
                            </el-button>
                        </div>
                    </template>

                    <el-table :data="filteredRecentTools" style="width: 100%" border stripe>
                        <el-table-column prop="tool_name" label="工具名称" />
                        <el-table-column prop="description" label="描述" :show-overflow-tooltip="true" />
                        <el-table-column label="参数">
                            <template #default="scope">
                                {{ scope.row.parameters }}
                            </template>
                        </el-table-column>
                        <el-table-column label="结果">
                            <template #default="scope">
                                <el-text type="success" truncated v-if="scope.row.status === 'success'">
                                    {{ scope.row.result }}
                                </el-text>
                                <el-text type="danger" truncated v-else>
                                    {{ scope.row.result }}
                                </el-text>
                            </template>
                        </el-table-column>
                        <el-table-column label="执行时间" width="180">
                            <template #default="scope">
                                {{ scope.row.created_at }}
                            </template>
                        </el-table-column>
                        <el-table-column label="耗时" width="100">
                            <template #default="scope">
                                {{ (scope.row.execution_time * 1000).toFixed(1) }}ms
                            </template>
                        </el-table-column>
                        <el-table-column prop="status" label="状态" width="100">
                            <template #default="scope">
                                <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                                    {{ scope.row.status === 'success' ? '成功' : '失败' }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column fixed="right" label="操作" width="180">
                            <template #default="scope">
                                <el-button link type="primary" @click="goToTool(scope.row.tool_name)">
                                    再次使用
                                </el-button>
                                <el-button v-if="scope.row.result" link type="primary" @click="showResult(scope.row)">
                                    查看结果
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <div v-if="filteredRecentTools.length === 0" class="empty-data">
                        <el-empty description="暂无执行记录"></el-empty>
                    </div>

                    <div class="pagination-container">
                        <el-pagination
                            :current-page="currentPage"
                            :page-size="pageSize"
                            :page-sizes="[10, 20, 50, 100]"
                            :total="total"
                            layout="total, sizes, prev, pager, next"
                            @size-change="handleSizeChange"
                            @current-change="handleCurrentChange"
                        />
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 结果对话框 -->
        <el-dialog v-model="resultDialogVisible" title="执行结果" width="50%">
            <pre class="result-content">{{ currentResult }}</pre>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {
    Tools, Suitcase, DataAnalysis, Timer,
    ArrowRight, Connection, Plus, Refresh, Search
} from '@element-plus/icons-vue'

// 定义自定义类型
interface RecentActivity {
    id: number;
    content: string;
    activity_type: string;
    related_id: number | null;
    created_at: string;
}

interface RecentToolExecution {
    id: number;
    tool_name: string;
    description: string;
    parameters: Record<string, any>;
    result: any;
    status: 'success' | 'failed';
    created_at: string;
    execution_time: number;
}

interface ToolInfo {
    name: string;
    doc: string;
}

const router = useRouter()
const searchQuery = ref('')
const resultDialogVisible = ref(false)
const currentResult = ref('')

// 统计数据
const moduleCount = ref(0)
const toolCount = ref(0)
const executionCount = ref(0)
const lastUpdateTime = ref('--')
const loading = ref({
    activities: false,
    executions: false,
    stats: false
})

// 收藏/常用工具
const favoriteTools = ref<ToolInfo[]>([])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 最近执行的工具
const recentTools = ref<RecentToolExecution[]>([])

const filteredRecentTools = computed(() => {
    return recentTools.value
})

// 方法
const goToTool = (toolName: string) => {
    router.push({
        name: 'Tools',
        query: { tool: toolName }
    })
}

const showResult = (tool: RecentToolExecution) => {
    currentResult.value = JSON.stringify(tool.result, null, 2) || ''
    resultDialogVisible.value = true
}

const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
}

// 格式化时间显示
const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return '刚刚'

    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}分钟前`

    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}小时前`

    const days = Math.floor(hours / 24)
    if (days < 30) return `${days}天前`

    const months = Math.floor(days / 30)
    if (months < 12) return `${months}个月前`

    return `${Math.floor(months / 12)}年前`
}

// 获取模块数量
const fetchModuleCount = async () => {
    try {
        const response = await axios.get('/api/modules/count')
        moduleCount.value = response.data.count
    } catch (error) {
        console.error('获取模块数量失败:', error)
    }
}

// 获取工具数量
const fetchToolCount = async () => {
    try {
        const response = await axios.get('/api/tools')
        toolCount.value = response.data.length
    } catch (error) {
        console.error('获取工具数量失败:', error)
    }
}

// 获取最近执行记录
const fetchRecentExecutions = async () => {
    loading.value.executions = true
    try {
        const response = await axios.get('/api/history/executions', {
            params: {
                page: currentPage.value,
                page_size: pageSize.value,
                tool_name: searchQuery.value || undefined
            }
        })
        recentTools.value = response.data.data
        total.value = response.data.total
    } catch (error) {
        console.error('获取执行记录失败:', error)
    } finally {
        loading.value.executions = false
    }
}

// 获取统计信息
const fetchStats = async () => {
    loading.value.stats = true
    try {
        const response = await axios.get('/api/history/stats')
        executionCount.value = response.data.execution_count || 0

        if (response.data.last_execution_time) {
            lastUpdateTime.value = formatTimeAgo(response.data.last_execution_time)
        } else {
            lastUpdateTime.value = '无记录'
        }
    } catch (error) {
        console.error('获取统计信息失败:', error)
    } finally {
        loading.value.stats = false
    }
}

// 获取常用工具
const fetchFavoriteTools = async () => {
    try {
        const response = await axios.get('/api/tools')
        favoriteTools.value = response.data.slice(0, 6)
    } catch (error) {
        console.error('获取常用工具失败:', error)
    }
}

// 处理分页变化
const handleSizeChange = (val: number) => {
    pageSize.value = val
    fetchRecentExecutions()
}

const handleCurrentChange = (val: number) => {
    currentPage.value = val
    fetchRecentExecutions()
}

// 监听搜索输入变化
// watch(searchQuery, () => {
//     currentPage.value = 1 // 重置到第一页
//     fetchRecentExecutions()
// })

// 刷新所有数据
const refreshData = () => {
    fetchModuleCount()
    fetchToolCount()
    fetchRecentExecutions()
    fetchStats()
    fetchFavoriteTools()
}

onMounted(() => {
    // 加载所有数据
    refreshData()
})
</script>

<style scoped lang="scss">
.home-container {
    padding: 20px;
}

.mt-20 {
    margin-top: 20px;
}

.mt-15 {
    margin-top: 15px;
}

.ml-5 {
    margin-left: 5px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* 统计卡片样式 */
.statistic-card {
    display: flex;
    padding: 10px;
    height: 120px;
    overflow: hidden;
    transition: all 0.3s;

    &:hover {
        transform: translateY(-5px);
    }
}


.icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    border-radius: 12px;
    margin-right: 15px;
}

.icon-container .el-icon {
    font-size: 32px;
    color: white;
}

.tool-icon {
    background-color: #409EFF;
}

.module-icon {
    background-color: #67C23A;
}

.run-icon {
    background-color: #E6A23C;
}

.update-icon {
    background-color: #F56C6C;
}

.statistic-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.statistic-value {
    font-size: 28px;
    font-weight: bold;
    line-height: 1;
    margin-bottom: 8px;
}

.statistic-title {
    font-size: 14px;
    color: #909399;
}

/* 工具卡片网格 */
.tool-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 15px;
}

.tool-card {
    cursor: pointer;
    transition: all 0.3s;
    height: 120px;

    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    }
}

.tool-card-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 10px;

    .el-icon {
        font-size: 24px;
        margin-bottom: 8px;
        color: #409EFF;
    }

    h3 {
        margin: 0 0 5px;
        font-size: 14px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
    }

    p {
        margin: 0;
        font-size: 12px;
        color: #909399;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
    }
}

.add-tool {
    .el-icon {
        font-size: 28px;
        color: #DCDFE6;
    }

    h3 {
        color: #DCDFE6;
    }
}

/* 搜索框 */
.search-input {
    width: 250px;
}

.search-button {
    margin-left: 10px;
}

/* 结果显示 */
.result-content {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    max-height: 400px;
    overflow: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: monospace;
}

/* 响应式调整 */
@media (max-width: 1400px) {
    .tool-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}

@media (max-width: 992px) {
    .tool-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 768px) {
    .tool-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 576px) {
    .tool-grid {
        grid-template-columns: 1fr;
    }
}

/* 分页容器 */
.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
</style>