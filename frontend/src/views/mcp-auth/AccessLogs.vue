<template>
    <div class="access-logs-page">
        <!-- <div class="page-header">
            <h1>访问日志</h1>
            <p class="page-description">查看MCP服务的访问记录和统计信息</p>
        </div> -->

        <div class="content-container">
            <!-- 服务选择和过滤器 -->
            <ActionSearchCard>
                <template #search>
                    <el-form :model="queryPage.condition" :inline="true" label-width="80px">
                        <el-form-item label="">
                            <el-select v-model="queryPage.condition.service_id" placeholder="请选择服务" style="width: 200px"
                                @change="handleServiceChange" clearable>
                                <el-option v-for="(service, index) in services" :key="index"
                                    :label="index + 1 + '. ' + service.name" :value="service.id" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="">
                            <el-select v-model="queryPage.condition.secret_id" placeholder="选择密钥" clearable
                                style="width: 200px" :disabled="!queryPage.condition.service_id">
                                <el-option v-for="(secret, index) in secrets" :key="index"
                                    :label="index + 1 + '. ' + secret.secret_name" :value="secret.id" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="">
                            <el-select v-model="queryPage.condition.status" placeholder="选择状态" clearable
                                style="width: 120px">
                                <el-option label="成功" value="success" />
                                <el-option label="失败" value="error" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="">
                            <el-date-picker v-model="queryPage.condition.date_range" type="datetimerange"
                                range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" clearable />
                        </el-form-item>
                        <el-form-item>

                        </el-form-item>
                    </el-form>
                </template>
                <template #actions>
                    <el-button type="primary" @click="loadLogs" :loading="loading">
                        查询
                    </el-button>
                    <el-button @click="resetFilters">
                        重置
                    </el-button>
                </template>
            </ActionSearchCard>

            <!-- 日志列表 -->
            <el-card class="logs-card">
                <!-- <template #header>
                    <div class="flex justify-between items-center">
                        <h3>访问日志</h3>
                        <el-button type="primary" size="small" @click="exportLogs" :disabled="logs.length === 0">
                            导出日志
                        </el-button>
                    </div>
                </template> -->

                <el-table :data="logs" style="width: 100%" v-loading="loading" max-height="600">
                    <el-table-column label="序号" width="80" align="center">
                        <template #default="{ $index, row }">
                            <div :class="[
                                'index-cell',
                                row.status === 'success' ? 'index-cell-success' :
                                    row.status === 'error' ? 'index-cell-danger' :
                                        'index-cell'
                            ]">
                                {{ $index + 1 }}
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column prop="access_time" label="访问时间" width="160" sortable>
                        <template #default="{ row }">
                            {{ formatDateTime(row.access_time) }}
                        </template>
                    </el-table-column>
                    <el-table-column prop="client_ip" label="客户端IP" width="120" />
                    <el-table-column prop="secret_name" label="使用密钥" width="150">
                        <template #default="{ row }">
                            <span v-if="row.secret_name">
                                {{ row.secret_name }}
                            </span>
                            <span v-else-if="row.secret_id">
                                秘钥ID：{{ row.secret_id }}
                            </span>
                            <span v-else>
                                未使用密钥
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态" width="90">
                        <template #default="{ row }">
                            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                                {{ row.status === 'success' ? '成功' : '失败' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip>
                        <template #default="{ row }">
                            <span v-if="row.error_message" class="text-red-500">
                                {{ row.error_message }}
                            </span>
                            <span v-else>
                                -
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="user_agent" label="用户代理" width="200" show-overflow-tooltip />
                    <el-table-column label="操作" width="100">
                        <template #default="{ row }">
                            <el-button size="small" @click="showLogDetail(row)">
                                详情
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <!-- 分页组件 -->
                <div v-if="!loading && total > 0" class="pagination-container">
                    <el-pagination :current-page="queryPage.paging.page" :page-size="queryPage.paging.size"
                        :page-sizes="[10, 20, 50, 100]" :background="true"
                        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
                        @current-change="handleCurrentChange" class="pagination" />
                </div>
            </el-card>
        </div>

        <!-- 日志详情对话框 -->
        <el-dialog v-model="detailVisible" title="访问详情" width="600px">
            <div v-if="currentLog">
                <el-descriptions :column="1" border>
                    <el-descriptions-item label="访问时间">
                        {{ formatDateTime(currentLog.access_time) }}
                    </el-descriptions-item>
                    <el-descriptions-item label="客户端IP">
                        {{ currentLog.client_ip }}
                    </el-descriptions-item>
                    <el-descriptions-item label="使用密钥">
                        {{ currentLog.secret_name || '未使用密钥' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="状态">
                        <el-tag :type="currentLog.status === 'success' ? 'success' : 'danger'" size="small">
                            {{ currentLog.status === 'success' ? '成功' : '失败' }}
                        </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="错误信息" v-if="currentLog.error_message">
                        <span class="text-red-500">{{ currentLog.error_message }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="用户代理">
                        {{ currentLog.user_agent }}
                    </el-descriptions-item>
                </el-descriptions>

                <div class="mt-4" v-if="currentLog.request_headers">
                    <h4>请求头信息</h4>
                    <el-input v-model="formattedHeaders" type="textarea" :rows="6" readonly />
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { mcpAuthApi } from '@/api/mcp-auth'
import { listServices } from '@/api/mcp'
import ActionSearchCard from '@/components/ActionSearchCard.vue';

// 响应式数据
const services = ref([])
const secrets = ref([])
const logs = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentLog = ref(null)
const total = ref(0)

// 分页相关状态
const queryPage = ref({
    paging: {
        page: 1,
        size: 20
    },
    condition: {
        service_id: null,
        secret_id: null,
        status: null,
        date_range: null
    }
});

// 统计数据
const stats = reactive({
    total_requests: 0,
    success_requests: 0,
    error_requests: 0,
    success_rate: 0
})

// 计算属性
const formattedHeaders = computed(() => {
    if (!currentLog.value?.request_headers) return ''

    try {
        const headers = typeof currentLog.value.request_headers === 'string'
            ? JSON.parse(currentLog.value.request_headers)
            : currentLog.value.request_headers

        return Object.entries(headers)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n')
    } catch (error) {
        return currentLog.value.request_headers
    }
})

// 方法
const loadServices = async () => {
    try {
        // 这里应该调用获取服务列表的API
        const response = await listServices();
        services.value = response.data || []
    } catch (error) {
        ElMessage.error('加载服务列表失败')
        console.error('Load services error:', error)
    }
}

const handleServiceChange = async (serviceId) => {
    if (serviceId) {
        await loadSecrets(serviceId)
        await loadLogs()
    }
}

const loadSecrets = async (serviceId) => {
    try {
        const response = await mcpAuthApi.getSecrets(serviceId)
        secrets.value = response.data || []
    } catch (error) {
        console.error('Load secrets error:', error)
    }
}

const loadLogs = async () => {
    if (!queryPage.value.condition.service_id) {
        ElMessage.warning('请先选择服务')
        return
    }

    loading.value = true
    try {
        // 移除空值
        const params = { ...queryPage.value }
        Object.keys(params.condition).forEach(key => {
            if (params.condition[key] === null || params.condition[key] === undefined || params.condition[key] === '') {
                delete params.condition[key]
            }
        })

        const data = await mcpAuthApi.getAccessLogs(queryPage.value.condition.service_id, params)
        logs.value = data.data || []
        total.value = data.total || 0

        // 更新统计数据
        updateStats()
    } catch (error) {
        ElMessage.error('加载访问日志失败')
        console.error('Load access logs error:', error)
    } finally {
        loading.value = false
    }
}

const updateStats = () => {
    stats.total_requests = logs.value.length
    stats.success_requests = logs.value.filter(log => log.status === 'success').length
    stats.error_requests = logs.value.filter(log => log.status === 'error').length
    stats.success_rate = stats.total_requests > 0
        ? Math.round((stats.success_requests / stats.total_requests) * 100)
        : 0
}

const resetFilters = () => {
    queryPage.value.condition.service_id = null
    queryPage.value.condition.secret_id = null
    queryPage.value.condition.status = null
    queryPage.value.condition.date_range = null
    secrets.value = []
    logs.value = []
    queryPage.value.paging.page = 1
}

const showLogDetail = (log) => {
    currentLog.value = log
    detailVisible.value = true
}

const formatDateTime = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleString()
}

const handleSizeChange = (size) => {
    queryPage.value.paging.size = size
    queryPage.value.paging.page = 1
    loadLogs()
}

const handleCurrentChange = (current) => {
    queryPage.value.paging.page = current
    loadLogs()
}

const exportLogs = () => {
    // 导出日志功能
    const csvContent = logs.value.map(log => {
        return [
            log.access_time,
            log.client_ip,
            log.secret_name || '',
            log.status,
            log.error_message || '',
            log.user_agent || ''
        ].join(',')
    }).join('\n')

    const header = 'Access Time,Client IP,Secret Name,Status,Error Message,User Agent\n'
    const csv = header + csvContent

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `access_logs_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('日志导出成功')
}

// 生命周期
onMounted(() => {
    loadServices()
})
</script>

<style scoped>
.access-logs-page {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 30px;
}

.page-header h1 {
    font-size: 28px;
    color: #303133;
    margin: 0 0 10px 0;
    font-weight: 600;
}

.page-description {
    color: #606266;
    font-size: 14px;
    margin: 0;
}

.content-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.filter-card,
.stats-card,
.logs-card {
    margin-bottom: 20px;
}

.text-red-500 {
    color: #ef4444;
}

.mt-4 {
    margin-top: 16px;
}

.flex {
    display: flex;
}

.justify-between {
    justify-content: space-between;
}

.items-center {
    align-items: center;
}

@media (max-width: 768px) {
    .access-logs-page {
        padding: 15px;
    }

    .page-header h1 {
        font-size: 24px;
    }
}
</style>