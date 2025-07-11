_<template>
    <div class="form-container">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
            <el-form-item label="启用鉴权" prop="auth_required">
                <el-switch v-model="form.auth_required" active-text="启用" inactive-text="禁用"
                    @change="handleAuthRequiredChange" />
                <div class="form-item-tip">
                    启用后，访问此服务需要提供有效的密钥
                </div>
            </el-form-item>

            <el-form-item v-if="form.auth_required" label="鉴权模式" prop="auth_mode">
                <el-radio-group v-model="form.auth_mode">
                    <el-radio label="secret">密钥鉴权</el-radio>
                    <el-radio label="token" disabled>令牌鉴权（待实现）</el-radio>
                </el-radio-group>
                <div class="form-item-tip">
                    选择鉴权验证方式
                </div>
            </el-form-item>

            <el-form-item v-if="form.auth_required && form.auth_mode === 'secret'" label="密钥管理">
                <div class="secret-management">
                    <!-- <div class="secret-info">
            <el-descriptions :column="2" size="small" border>
              <el-descriptions-item label="已创建密钥">
                {{ secretCount }}个
              </el-descriptions-item>
              <el-descriptions-item label="活跃密钥">
                {{ activeSecretCount }}个
              </el-descriptions-item>
              <el-descriptions-item label="最后访问">
                {{ lastAccessTime || '暂无访问' }}
              </el-descriptions-item>
              <el-descriptions-item label="总访问次数">
                {{ totalAccessCount }}次
              </el-descriptions-item>
            </el-descriptions>
          </div> -->
                    <div class="secret-actions">
                        <el-button type="primary" @click="$emit('manage-secrets')">
                            管理密钥
                        </el-button>
                        <el-button @click="$emit('view-logs')">
                            查看日志
                        </el-button>
                    </div>
                </div>
            </el-form-item>

            <el-form-item v-if="form.auth_required" label="访问说明">
                <div class="form-field-group">
                    <div class="field-group-title">如何使用密钥访问服务</div>
                    <!-- <div class="field-group-description">请选择以下任一方式进行身份验证</div> -->
                    <el-form-item label="服务地址" class="form-item">
                        <el-input :value="`${serviceUrl}`" readonly size="small" />
                    </el-form-item>
                    
                    <el-form-item label="Authorization头" class="form-item">
                        <el-input :value="`Authorization: your_secret_key`" readonly size="small" />
                        <div class="form-item-tip">在请求头中添加 Authorization 字段</div>
                    </el-form-item>


                    <el-form-item label="示例（curl）" class="form-item">
                        <el-input :value="curlExample" type="textarea" :rows="3" readonly size="small" />
                        <div class="form-item-tip">使用 curl 命令测试服务访问</div>
                    </el-form-item>
                </div>
            </el-form-item>

            <div class="form-actions">
                <el-button type="primary" @click="submitForm" :loading="loading">
                    保存配置
                </el-button>
                <el-button @click="resetForm">
                    重置
                </el-button>
            </div>
        </el-form>
    </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { mcpAuthApi } from '@/api/mcp-auth'

// Props
const props = defineProps({
    serviceId: {
        type: Number,
        required: true
    },
    serviceUrl: {
        type: String,
        default: ''
    },
    loading: {
        type: Boolean,
        default: false
    }
})

// Emits
const emit = defineEmits(['update:loading', 'manage-secrets', 'view-logs', 'config-updated'])

// Reactive data
const formRef = ref(null)
const secretCount = ref(0)
const activeSecretCount = ref(0)
const lastAccessTime = ref('')
const totalAccessCount = ref(0)
const secretStatistics = ref({})

// Form data
const form = reactive({
    auth_required: false,
    auth_mode: 'secret'
})

const originalForm = reactive({
    auth_required: false,
    auth_mode: 'secret'
})

// Form rules
const rules = {
    auth_mode: [
        { required: true, message: '请选择鉴权模式', trigger: 'change' }
    ]
}

// Computed
const curlExample = computed(() => {
    if (!props.serviceUrl) return ''

    return `curl -H "Authorization: your_secret_key" \\
     -H "Content-Type: application/json" \\
     "${props.serviceUrl}"`
})

// Watch
watch(() => props.serviceId, (newId) => {
    if (newId) {
        loadAuthConfig()
        loadSecretSummary()
    }
})

// Methods
const loadAuthConfig = async () => {
    try {
        const response = await mcpAuthApi.getAuthConfig(props.serviceId)
        const config = response.data || {}

        form.auth_required = config.auth_required || false
        form.auth_mode = config.auth_mode || 'secret'

        // 保存原始配置
        Object.assign(originalForm, form)
    } catch (error) {
        console.error('Load auth config error:', error)
        ElMessage.error('加载鉴权配置失败')
    }
}

const loadSecretStatistics = async () => {
    try {
        const response = await mcpAuthApi.getSecretStatistics(props.serviceId)
        const statistics = response.data || {}
    } catch (error) {
        console.error('Load secret statistics error:', error)
    }
}

const loadSecretSummary = async () => {
    try {
        const response = await mcpAuthApi.getSecrets(props.serviceId)
        const secrets = response.data || []

        secretCount.value = secrets.length
        activeSecretCount.value = secrets.filter(s => s.is_active).length

        // 获取最后访问时间（这里简化处理，实际应该从统计数据获取）
        const activeSEcrets = secrets.filter(s => s.is_active)
        if (activeSEcrets.length > 0) {
            // 这里可以进一步调用统计API获取更详细的信息
            //   lastAccessTime.value = secrets.filter(s => s.is_active).sort((a, b) => new Date(b.last_access_time) - new Date(a.last_access_time))[0].last_access_time
            //   totalAccessCount.value = secrets.f
        }
    } catch (error) {
        console.error('Load secret summary error:', error)
    }
}

const handleAuthRequiredChange = (value) => {
    if (value && !form.auth_mode) {
        form.auth_mode = 'secret'
    }
}

const submitForm = async () => {
    if (!formRef.value) return

    const valid = await formRef.value.validate()
    if (!valid) return

    emit('update:loading', true)

    try {
        await mcpAuthApi.updateAuthConfig(props.serviceId, {
            auth_required: form.auth_required,
            auth_mode: form.auth_required ? form.auth_mode : ''
        })

        // 更新原始配置
        Object.assign(originalForm, form)

        ElMessage.success('鉴权配置保存成功')
        emit('config-updated', { ...form })
    } catch (error) {
        console.error('Update auth config error:', error)
        ElMessage.error('保存鉴权配置失败')
    } finally {
        emit('update:loading', false)
    }
}

const resetForm = () => {
    Object.assign(form, originalForm)
    formRef.value?.clearValidate()
}

// 初始化
if (props.serviceId) {
    loadAuthConfig()
    loadSecretSummary()
}

// 暴露方法给父组件
defineExpose({
    loadAuthConfig,
    loadSecretSummary
})
</script>

<style scoped>
.secret-management {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.secret-info {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
}

.secret-actions {
  display: flex;
  gap: 10px;
}

/* 移除原有的访问说明样式，使用全局表单样式 */
</style>