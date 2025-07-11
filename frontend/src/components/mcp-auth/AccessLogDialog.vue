<template>
    <el-dialog v-model="dialogVisible" title="访问日志" width="60%" :close-on-click-modal="false" @close="handleClose">
        <div class="access-log-container">
            <!-- 过滤器 -->
            <ActionSearchCard>
                <template #search>
                    <el-select v-model="queryPage.condition.secret_id" placeholder="选择密钥" clearable
                        style="width: 200px">
                        <el-option v-for="secret in secrets" :key="secret.id" :label="secret.secret_name"
                            :value="secret.id" />
                    </el-select>
                    <el-select v-model="queryPage.condition.status" placeholder="选择状态" clearable style="width: 120px">
                        <el-option label="成功" value="success" />
                        <el-option label="失败" value="error" />
                    </el-select>
                </template>
                <template #actions>
                    <el-button type="primary" @click="loadAccessLogs" :loading="loading">
                        查询
                    </el-button>
                    <el-button @click="resetFilters">
                        重置
                    </el-button>
                </template>
            </ActionSearchCard>

            <!-- 日志列表 -->
            <div class="mt-16">
                <el-table :data="logs" style="width: 100%" v-loading="loading" max-height="500">
                    <el-table-column label="序号" width="80" align="center">
                        <template #default="scope">
                            <div class="index-cell">
                                {{ scope.$index + 1 }}
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column prop="access_time" label="访问时间" width="160">
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
                            <span v-else class="text-gray-500">
                                未使用密钥
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态" width="80">
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
                            <span v-else class="text-gray-500">
                                -
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="user_agent" label="用户代理" width="170" show-overflow-tooltip />
                    <el-table-column label="操作" width="100">
                        <template #default="{ row }">
                            <el-button size="small" @click="showLogDetail(row)">
                                详情
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
            <!-- 分页组件 -->
            <div v-if="!loading && total > 0" class="pagination-container mt-16">
                <el-config-provider :locale="zhCn">
                    <el-pagination :current-page="queryPage.paging.page" :page-size="queryPage.paging.size"
                        :page-sizes="[10, 20, 50, 100]" :background="true" layout="total, sizes, prev, pager, next, jumper"
                        :total="total" @size-change="handleSizeChange" @current-change="handleCurrentChange"
                        class="pagination" />
                </el-config-provider>
            </div>
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
    </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { mcpAuthApi } from '@/api/mcp-auth'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { defineAsyncComponent } from 'vue';
const ActionSearchCard = defineAsyncComponent(() => import('@/components/ActionSearchCard.vue'));
// Props
const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    serviceId: {
        type: Number,
        required: true
    }
})

// Emits
const emit = defineEmits(['update:visible'])

// Reactive data
const dialogVisible = ref(false)
const detailVisible = ref(false)
const loading = ref(false)
const logs = ref([])
const secrets = ref([])
const currentLog = ref(null)
const total = ref(0)

// 分页相关状态
const queryPage = ref({
    paging: {
        page: 1,
        size: 20
    },
    condition: {
        service_id: props.serviceId,
        secret_id: null,
        status: null
    }
});

// Watch props
watch(() => props.visible, (val) => {
    dialogVisible.value = val
    if (val) {
        loadSecrets()
        loadAccessLogs()
    }
})

watch(dialogVisible, (val) => {
    emit('update:visible', val)
})

// Computed
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

// Methods
const loadSecrets = async () => {
    try {
        const response = await mcpAuthApi.getSecrets(props.serviceId)
        secrets.value = response.data || []
    } catch (error) {
        console.error('Load secrets error:', error)
    }
}

const loadAccessLogs = async () => {
    loading.value = true
    try {
        // 移除空值
        const params = { ...queryPage.value }
        Object.keys(params.condition).forEach(key => {
            if (params.condition[key] === null || params.condition[key] === undefined || params.condition[key] === '') {
                delete params.condition[key]
            }
        })

        const data = await mcpAuthApi.getAccessLogs(props.serviceId, params)
        logs.value = data.data || []
        total.value = data.total || 0
    } catch (error) {
        ElMessage.error('加载访问日志失败')
        console.error('Load access logs error:', error)
    } finally {
        loading.value = false
    }
}

const resetFilters = () => {
    queryPage.value.condition.secret_id = null
    queryPage.value.condition.status = null
    queryPage.value.paging.page = 1
    loadAccessLogs()
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
    loadAccessLogs()
}

const handleCurrentChange = (current) => {
    queryPage.value.paging.page = current
    loadAccessLogs()
}

const handleClose = () => {
    dialogVisible.value = false
}
</script>

<style scoped>
.access-log-container {
    min-height: 400px;
}

.text-gray-500 {
    color: #9ca3af;
}

.text-red-500 {
    color: #ef4444;
}
</style>