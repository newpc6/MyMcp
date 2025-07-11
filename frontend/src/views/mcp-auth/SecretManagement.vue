<template>
    <div class="secret-management-page">
        <!-- <div class="page-header">
            <h1>密钥管理</h1>
            <p class="page-description">管理MCP服务的访问密钥，监控使用情况</p>
        </div> -->

        <div class="content-container">
            <!-- 服务选择器 -->
            <div class="service-selector">
                <el-card shadow="never" class="card-form card-accent">
                    <template #header>
                        <div class="card-header">
                            <h3>服务选择</h3>
                        </div>
                    </template>
                    <el-select v-model="selectedServiceId" placeholder="请选择要管理的服务" style="width: 100%"
                        @change="handleServiceChange">
                        <el-option v-for="(service, index) in services" :key="service.id"
                            :label="`${index + 1}. ${service.name || service.module_name} (${service.service_uuid})`"
                            :value="service.id" />
                    </el-select>
                </el-card>
            </div>

            <!-- 密钥管理内容 -->
            <div v-if="selectedServiceId" class="management-content">
                <el-row :gutter="20">
                    <!-- 鉴权配置 -->
                    <el-col :span="12">
                        <el-card class="card-content card-accent accent-info">
                            <template #header>
                                <div class="card-header">
                                    <h3>鉴权配置</h3>
                                </div>
                            </template>
                            <AuthConfigForm :service-id="selectedServiceId" :service-url="serviceUrl"
                                :loading="authConfigLoading" @update:loading="authConfigLoading = $event"
                                @manage-secrets="showSecretManageDialog" @view-logs="showAccessLogDialog"
                                @config-updated="handleAuthConfigUpdated" ref="authConfigRef" />
                        </el-card>
                    </el-col>

                    <!-- 统计信息 -->
                    <el-col :span="12">
                        <el-card class="card-info card-data card-accent accent-success">
                            <template #header>
                                <div class="card-header">
                                    <h3>访问统计</h3>
                                </div>
                            </template>
                            <div class="info-content">
                                <el-row :gutter="16">
                                    <el-col :span="12">
                                        <div class="data-item">
                                            <div class="data-value">{{ statistics.total_secrets || 0 }}</div>
                                            <div class="data-label">总密钥数</div>
                                        </div>
                                    </el-col>
                                    <el-col :span="12">
                                        <div class="data-item">
                                            <div class="data-value">{{ statistics.active_secrets || 0 }}</div>
                                            <div class="data-label">启用密钥</div>
                                        </div>
                                    </el-col>
                                    <el-col :span="12">
                                        <div class="data-item">
                                            <div class="data-value">{{ statistics.inactive_secrets || 0 }}</div>
                                            <div class="data-label">停用密钥</div>
                                        </div>
                                    </el-col>
                                    <el-col :span="12">
                                        <div class="data-item">
                                            <div class="data-value">{{ statistics.total_calls || 0 }}</div>
                                            <div class="data-label">总调用次数</div>
                                        </div>
                                    </el-col>
                                    <el-col :span="12">
                                        <div class="data-item">
                                            <div class="data-value">{{ statistics.total_success_count || 0 }}</div>
                                            <div class="data-label">成功次数</div>
                                        </div>
                                    </el-col>
                                    <el-col :span="12">
                                        <div class="data-item">
                                            <div class="data-value">{{ statistics.success_rate || 0 }}%</div>
                                            <div class="data-label">成功率</div>
                                        </div>
                                    </el-col>
                                    <el-col :span="24">
                                        <div class="data-item">
                                            <div class="data-value">{{ statistics.last_access_time || '--' }}</div>
                                            <div class="data-label">最后访问时间</div>
                                        </div>
                                    </el-col>
                                </el-row>
                            </div>
                        </el-card>
                    </el-col>
                </el-row>
            </div>

            <!-- 空状态 -->
            <div v-else class="empty-state">
                <el-card class="card-empty card-hover">
                    <el-empty description="请先选择一个启用了鉴权的服务">
                        <el-button type="primary" @click="loadServices">刷新服务列表</el-button>
                    </el-empty>
                </el-card>
            </div>
        </div>

        <!-- 密钥管理对话框 -->
        <SecretManageDialog :visible="secretManageVisible" :service-id="selectedServiceId"
            @update:visible="secretManageVisible = $event" @secrets-updated="loadStatistics" />

        <!-- 访问日志对话框 -->
        <AccessLogDialog :visible="accessLogVisible" :service-id="selectedServiceId"
            @update:visible="accessLogVisible = $event" />
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthConfigForm from '@/components/mcp-auth/AuthConfigForm.vue'
import SecretManageDialog from '@/components/mcp-auth/SecretManageDialog.vue'
import AccessLogDialog from '@/components/mcp-auth/AccessLogDialog.vue'
import { mcpAuthApi } from '@/api/mcp-auth'
import { listServices } from '@/api/mcp'

const route = useRoute()
const router = useRouter()

// 响应式数据
const services = ref([])
const selectedServiceId = ref(null)
const authConfigLoading = ref(false)
const secretManageVisible = ref(false)
const accessLogVisible = ref(false)
const statistics = ref({
    total_secrets: 0,
    active_secrets: 0,
    inactive_secrets: 0,
    total_calls: 0,
    total_success_count: 0,
    success_rate: 0,
    last_access_time: 0
})

// 计算属性
const currentService = computed(() => {
    return services.value.find(s => s.id === selectedServiceId.value)
})

const serviceUrl = computed(() => {
    return currentService.value?.sse_url || ''
})

// 引用
const authConfigRef = ref(null)

// 方法
const loadServices = async () => {
    try {
        const response = await listServices()
        services.value = response.data || []

        // 如果URL中有serviceId参数，自动选择该服务
        const serviceId = route.query.serviceId
        if (serviceId && services.value.length > 0) {
            const targetService = services.value.find(s => s.id === parseInt(serviceId))
            if (targetService) {
                selectedServiceId.value = targetService.id
            }
        }
    } catch (error) {
        console.error('加载服务列表失败:', error)
        ElMessage.error('加载服务列表失败')
    }
}

const handleServiceChange = (serviceId) => {
    selectedServiceId.value = serviceId
    // 更新URL查询参数
    router.replace({
        path: route.path,
        query: { ...route.query, serviceId: serviceId.toString() }
    })
    loadStatistics()
}

const loadStatistics = async () => {
    console.log('selectedServiceId.value', selectedServiceId.value)

    if (!selectedServiceId.value) return

    try {
        // 加载密钥统计信息
        const data = await mcpAuthApi.getSecretInfo(selectedServiceId.value)
        const result = data.data || {}

        statistics.value.total_secrets = result.secret_count
        statistics.value.active_secrets = result.active_secret_count
        statistics.value.inactive_secrets = result.inactive_secret_count
        // 这里可以进一步调用统计API获取更详细的信息
        statistics.value.total_calls = result.total_call_count
        statistics.value.total_success_count = result.total_success_count
        statistics.value.success_rate = result.total_success_count / result.total_call_count * 100
        statistics.value.last_access_time = result.last_access_time
    } catch (error) {
        console.error('Load statistics error:', error)
    }
}

const showSecretManageDialog = () => {
    if (!selectedServiceId.value) {
        ElMessage.warning('请先选择服务')
        return
    }
    secretManageVisible.value = true
}

const showAccessLogDialog = () => {
    if (!selectedServiceId.value) {
        ElMessage.warning('请先选择服务')
        return
    }
    accessLogVisible.value = true
}

const handleAuthConfigUpdated = () => {
    ElMessage.success('鉴权配置已更新')
    // 重新加载服务列表
    loadServices()
    loadStatistics()
}

// 生命周期
onMounted(() => {
    selectedServiceId.value = route.query.serviceId
    loadServices()
    loadStatistics()
})
</script>

<style scoped>
.secret-management-page {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 30px;
}

.page-header h1 {
    font-size: 28px;
    color: #1a202c;
    margin: 0 0 10px 0;
    font-weight: 600;
}

.page-description {
    color: #4a5568;
    font-size: 14px;
    margin: 0;
}

.content-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.service-selector {
    margin-bottom: 20px;
}

.management-content {
    flex: 1;
}

.empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
}

@media (max-width: 768px) {
    .secret-management-page {
        padding: 15px;
    }

    .page-header h1 {
        font-size: 24px;
    }
    
    .content-container {
        gap: 15px;
    }
    
    .service-selector {
        margin-bottom: 15px;
    }
}

@media (max-width: 576px) {
    .secret-management-page {
        padding: 10px;
    }
    
    .page-header h1 {
        font-size: 20px;
    }
}
</style>