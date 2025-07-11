<template>
    <el-dialog v-model="dialogVisible" title="密钥管理" width="60%" height="60%" :close-on-click-modal="false"
        @close="handleClose" draggable>
        <div class="secret-manage-container">
            <!-- 操作按钮 -->
            <div class="operation-bar">
                <el-button type="primary" icon="Plus" @click="showCreateDialog">
                    新增密钥
                </el-button>
                <el-button icon="Refresh" @click="loadSecrets">
                    刷新
                </el-button>
            </div>

            <!-- 密钥列表 -->
            <div class="secret-list">
                <el-table :data="secrets" style="width: 100%" v-loading="loading">
                    <el-table-column prop="secret_name" label="密钥名称" width="150" />
                    <el-table-column prop="secret_key" label="MCP密钥" width="200" show-overflow-tooltip>
                        <template #default="{ row }">
                            <div class="secret-key-display">
                                <el-button v-if="row.secret_key.includes('****')" size="small" text
                                    @click="copyFullSecret(row)">
                                    复制完整密钥
                                </el-button>
                                <el-button v-else size="small" text @click.stop="copySecret(row.secret_key)">
                                    复制
                                </el-button>
                                <span class="secret-key">{{ row.secret_key }}</span>
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" show-overflow-tooltip />
                    <el-table-column prop="is_active" label="状态" width="80">
                        <template #default="{ row }">
                            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                                {{ row.is_active ? '启用' : '禁用' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="limit_count" label="每日调用限制" width="130">
                        <template #default="{ row }">
                            <span v-if="row.limit_count > 0">
                                {{ row.limit_count }}
                            </span>
                            <span v-else class="text-gray-500">无限制</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="expires_at" label="过期时间" width="120">
                        <template #default="{ row }">
                            <span v-if="row.expires_at">
                                {{ formatDate(row.expires_at) }}
                            </span>
                            <span v-else class="text-gray-500">永不过期</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="created_at" label="创建时间" width="120">
                        <template #default="{ row }">
                            {{ formatDate(row.created_at) }}
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="230">
                        <template #default="{ row }">
                            <el-button size="small" type="primary" @click="showEditDialog(row)">
                                编辑
                            </el-button>
                            <el-button size="small" type="info" @click="showStatistics(row)">
                                统计
                            </el-button>
                            <el-button size="small" type="danger" @click="deleteSecret(row)">
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </div>

        <!-- 创建/编辑密钥对话框 -->
        <el-dialog v-model="secretFormVisible" :title="isEdit ? '编辑密钥' : '新增密钥'" width="500px"
            :close-on-click-modal="false">
            <el-form ref="secretFormRef" :model="secretForm" :rules="secretFormRules" label-width="100px">
                <el-form-item label="密钥名称" prop="name">
                    <el-input v-model="secretForm.name" placeholder="请输入密钥名称" clearable/>
                </el-form-item>
                <el-form-item label="描述" prop="description">
                    <el-input v-model="secretForm.description" type="textarea" :rows="3" placeholder="请输入密钥描述" clearable/>
                </el-form-item>
                <el-form-item label="有效期" prop="expires_days">
                    <el-select v-model="secretForm.expires_days" placeholder="请选择有效期，可手动输入天数" filterable allow-create clearable @change="handleExpiresDaysChange">
                        <el-option label="永不过期" :value="0" />
                        <el-option label="30天" :value="30" />
                        <el-option label="90天" :value="90" />
                        <el-option label="180天" :value="180" />
                        <el-option label="365天" :value="365" />
                    </el-select>
                </el-form-item>
                <el-form-item label="每日调用限制" prop="limit_count">
                    <el-input-number v-model="secretForm.limit_count" placeholder="请输入每日调用限制" clearable/>
                </el-form-item>
                <el-form-item label="状态" prop="is_active">
                    <el-switch v-model="secretForm.is_active" active-text="启用" inactive-text="禁用" />
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="secretFormVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitSecretForm" :loading="submitting">
                        确定
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 统计信息对话框 -->
        <el-dialog v-model="statisticsVisible" title="密钥统计" width="600px">
            <div v-if="currentSecret">
                <div class="statistics-summary">
                    <el-row :gutter="20">
                        <el-col :span="8">
                            <div class="stat-card">
                                <div class="stat-value">{{ statisticsData.total_calls || 0 }}</div>
                                <div class="stat-label">总调用次数</div>
                            </div>
                        </el-col>
                        <el-col :span="8">
                            <div class="stat-card">
                                <div class="stat-value">{{ statisticsData.success_calls || 0 }}</div>
                                <div class="stat-label">成功调用</div>
                            </div>
                        </el-col>
                        <el-col :span="8">
                            <div class="stat-card">
                                <div class="stat-value">{{ statisticsData.error_calls || 0 }}</div>
                                <div class="stat-label">失败调用</div>
                            </div>
                        </el-col>
                    </el-row>
                </div>
                <div class="statistics-chart">
                    <!-- 这里可以添加图表组件 -->
                    <el-empty description="图表功能待实现" />
                </div>
            </div>
        </el-dialog>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { mcpAuthApi } from '@/api/mcp-auth'
import { copyTextToClipboard } from '@/utils/copy'

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
const loading = ref(false)
const secrets = ref([])
const secretFormVisible = ref(false)
const statisticsVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentSecret = ref(null)
const statisticsData = ref({})

// Form data
const secretForm = reactive({
    name: '',
    description: '',
    expires_days: 0,
    limit_count: 0,
    is_active: true
})

const secretFormRules = {
    name: [
        { required: true, message: '请输入密钥名称', trigger: 'blur' },
        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
    ]
}

// Refs
const secretFormRef = ref(null)

// Watch props
watch(() => props.visible, (val) => {
    dialogVisible.value = val
    if (val) {
        loadSecrets()
    }
})

watch(dialogVisible, (val) => {
    emit('update:visible', val)
})

// Methods
const loadSecrets = async () => {
    loading.value = true
    try {
        const response = await mcpAuthApi.getSecrets(props.serviceId)
        secrets.value = response.data || []
    } catch (error) {
        ElMessage.error('加载密钥列表失败')
        console.error('Load secrets error:', error)
    } finally {
        loading.value = false
    }
}

const showCreateDialog = () => {
    isEdit.value = false
    resetSecretForm()
    secretFormVisible.value = true
}

const showEditDialog = (secret) => {
    isEdit.value = true
    currentSecret.value = secret
    secretForm.name = secret.secret_name
    secretForm.description = secret.description
    secretForm.expires_days = secret.expires_days
    secretForm.limit_count = secret.limit_count
    secretForm.is_active = secret.is_active
    secretFormVisible.value = true
}

const resetSecretForm = () => {
    Object.assign(secretForm, {
        name: '',
        description: '',
        expires_days: 0,
        limit_count: 0,
        is_active: true
    })
    currentSecret.value = null
}

const submitSecretForm = async () => {
    if (!secretFormRef.value) return

    const valid = await secretFormRef.value.validate()
    if (!valid) return

    submitting.value = true
    try {
        if (isEdit.value) {
            await mcpAuthApi.updateSecret(currentSecret.value.id, {
                name: secretForm.name,
                description: secretForm.description,
                is_active: secretForm.is_active,
                expires_days: secretForm.expires_days,
                limit_count: secretForm.limit_count
            })
            ElMessage.success('密钥更新成功')
        } else {
            const response = await mcpAuthApi.createSecret(props.serviceId, {
                name: secretForm.name,
                description: secretForm.description,
                is_active: secretForm.is_active,
                expires_days: secretForm.expires_days,
                limit_count: secretForm.limit_count
            })
            ElMessage.success('密钥创建成功')

            // 显示新创建的密钥
            if (response.data.secret_key) {
                ElMessageBox.alert(
                    `密钥创建成功！请保存好您的密钥：\n${response.data.secret_key}`,
                    '密钥信息',
                    {
                        confirmButtonText: '已保存',
                        type: 'success'
                    }
                )
            }
        }

        secretFormVisible.value = false
        loadSecrets()
    } catch (error) {
        ElMessage.error(isEdit.value ? '更新密钥失败' : '创建密钥失败')
        console.error('Submit secret form error:', error)
    } finally {
        submitting.value = false
    }
}

const deleteSecret = async (secret) => {
    try {
        await ElMessageBox.confirm(
            `确定要删除密钥 "${secret.secret_name}" 吗？`,
            '确认删除',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )

        await mcpAuthApi.deleteSecret(secret.id)
        ElMessage.success('密钥删除成功')
        loadSecrets()
    } catch (error) {
        if (error !== 'cancel') {
            ElMessage.error('删除密钥失败')
            console.error('Delete secret error:', error)
        }
    }
}

const showStatistics = async (secret) => {
    currentSecret.value = secret
    statisticsVisible.value = true

    try {
        const response = await mcpAuthApi.getSecretStatistics(secret.id, 30)
        statisticsData.value = response.data || {}
    } catch (error) {
        ElMessage.error('加载统计数据失败')
        console.error('Load statistics error:', error)
    }
}

const copySecret = (secretKey) => {
    copyTextToClipboard(secretKey, '秘钥已复制到剪贴板')
}

const copyFullSecret = (secret) => {
    // 这里应该重新获取完整密钥，但出于安全考虑，通常不会提供此功能
    ElMessage.warning('完整密钥只在创建时显示，请联系管理员')
}

const formatDate = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString()
}

const handleClose = () => {
    dialogVisible.value = false
}

const handleExpiresDaysChange = (value) => {
    // 如果是数字类型且为正整数，直接使用
    if (typeof value === 'number' && Number.isInteger(value) && value >= 0) {
        secretForm.expires_days = value
        return
    }
    
    // 如果是字符串，尝试转换为数字
    if (typeof value === 'string') {
        const numValue = parseInt(value, 10)
        if (!isNaN(numValue) && Number.isInteger(numValue) && numValue >= 0) {
            secretForm.expires_days = numValue
            return
        }
    }
    
    // 如果输入无效，重置为0（永不过期）
    // secretForm.expires_days = 0
    ElMessage.warning('请输入有效的天数（0或正整数）')
}
</script>

<style scoped>
.secret-manage-container {
    min-height: 400px;
}

.operation-bar {
    margin-bottom: 20px;
}

.secret-key-display {
    display: flex;
    align-items: center;
    gap: 10px;
}

.secret-key {
    font-family: monospace;
    font-size: 12px;
    color: #666;
}

.statistics-summary {
    margin-bottom: 20px;
}

.stat-card {
    text-align: center;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #409eff;
}

.stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 5px;
}

.statistics-chart {
    min-height: 200px;
}

.text-gray-500 {
    color: #9ca3af;
}
</style>