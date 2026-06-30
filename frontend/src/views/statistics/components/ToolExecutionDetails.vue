<template>
    <div class="tool-execution-details">
        <div class="detail-card">
            <div class="card-header">
                <div class="header-title">
                    <el-icon class="header-icon">
                        <DataAnalysis />
                    </el-icon>
                    工具调用详情
                </div>
                <div class="header-actions">
                    <el-input v-model="toolFilter" placeholder="按工具名筛选" clearable class="filter-input">
                        <template #prefix>
                            <el-icon>
                                <Search />
                            </el-icon>
                        </template>
                        <template #append>
                            <el-button @click="$emit('search', toolFilter)" class="search-append-btn">
                                <el-icon>
                                    <Search />
                                </el-icon>
                            </el-button>
                        </template>
                    </el-input>
                </div>
            </div>

            <div class="table-container">
                <el-table :data="toolExecutions.items" stripe style="width: 100%" v-loading="loading"
                    class="detail-table"
                    :header-cell-style="{ background: 'var(--common-table-header-background-color)', color: 'var(--common-text-color)', fontWeight: '600' }">
                    <el-table-column label="序号" width="60" align="center">
                        <template #default="scope">
                            <div class="ranking-badge ranking-normal">
                                {{ scope.$index + 1 }}
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="tool_name" label="工具名称">
                        <template #default="scope">
                            <div class="tool-info">
                                <span class="tool-name">{{ scope.row.tool_name }}</span>
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column label="所属服务">
                        <template #default="scope">
                            <el-tag v-if="scope.row.service && scope.row.service.name" size="small" type="primary"
                                effect="light" class="service-tag">
                                {{ scope.row.service.name }}
                            </el-tag>
                            <span v-else class="no-data">-</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="所属模块">
                        <template #default="scope">
                            <el-tag v-if="scope.row.module && scope.row.module.name" size="small" type="success"
                                effect="light" class="module-tag">
                                {{ scope.row.module.name }}
                            </el-tag>
                            <span v-else class="no-data">-</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="创建者">
                        <template #default="scope">
                            <span class="creator-name">{{ scope.row.creator_name || '-' }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态" width="100" align="center">
                        <template #default="scope">
                            <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'" size="small"
                                effect="light" class="status-tag">
                                {{ scope.row.status }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="execution_time" label="执行时间" align="right">
                        <template #default="scope">
                            <span class="execution-time">{{ scope.row.execution_time }} ms</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="created_at" label="创建时间" width="180">
                        <template #default="scope">
                            <span class="created-time">{{ formatDate(scope.row.created_at) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="100" align="center" fixed="right">
                        <template #default="scope">
                            <el-button type="primary" size="small" @click="showExecutionDetails(scope.row)"
                                class="details-button">
                                详情
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <div class="pagination-section">
                <el-config-provider :locale="zhCn">
                    <el-pagination size="small" :current-page="currentPage" :page-size="pageSize"
                        :page-sizes="[5, 10, 15, 20]" :background="true"
                        layout="total, sizes, prev, pager, next, jumper" :total="toolExecutions.total"
                        @size-change="handleSizeChange" @current-change="handleCurrentChange" />
                </el-config-provider>
            </div>
        </div>

        <!-- 执行详情对话框 -->
        <el-dialog v-model="detailsVisible" :title="`工具执行详情 - ${selectedExecution?.tool_name}`" width="70%"
            class="execution-dialog">
            <div v-if="selectedExecution" class="execution-content">
                <div class="execution-header">
                    <div class="execution-title">
                        <h3>{{ selectedExecution.tool_name }}</h3>
                        <el-tag :type="selectedExecution.status === 'success' ? 'success' : 'danger'" size="large"
                            effect="light">
                            {{ selectedExecution.status }}
                        </el-tag>
                    </div>
                    <div class="execution-meta">
                        <div class="meta-item">
                            <span class="meta-label">ID:</span>
                            <span class="meta-value">{{ selectedExecution.id }}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">执行时间:</span>
                            <span class="meta-value">{{ selectedExecution.execution_time }} ms</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">创建时间:</span>
                            <span class="meta-value">{{ formatDate(selectedExecution.created_at) }}</span>
                        </div>
                        <div v-if="selectedExecution.creator_name" class="meta-item">
                            <span class="meta-label">创建者:</span>
                            <span class="meta-value">{{ selectedExecution.creator_name }}</span>
                        </div>
                    </div>
                </div>

                <div class="content-section">
                    <h4>输入参数</h4>
                    <div class="code-container">
                        <pre>{{ formatJson(selectedExecution.input_params) }}</pre>
                    </div>
                </div>

                <div class="content-section">
                    <h4>执行结果</h4>
                    <div class="code-container">
                        <pre>{{ formatJson(selectedExecution.output_result) }}</pre>
                    </div>
                </div>

                <div v-if="selectedExecution.error_message" class="content-section">
                    <h4>错误信息</h4>
                    <div class="code-container error">
                        <pre>{{ selectedExecution.error_message }}</pre>
                    </div>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { DataAnalysis, Search } from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { getRankingClass } from '@/utils/table'
// 定义Props
defineProps({
    toolExecutions: {
        type: Object,
        default: () => ({
            items: [],
            total: 0,
            page: 1
        })
    },
    loading: {
        type: Boolean,
        default: false
    },
    currentPage: {
        type: Number,
        default: 1
    },
    pageSize: {
        type: Number,
        default: 10
    }
})

// 定义事件
const emit = defineEmits(['search', 'size-change', 'page-change'])

// 过滤器
const toolFilter = ref('')

// 详情对话框
const detailsVisible = ref(false)
const selectedExecution = ref(null)

// 显示调用详情
const showExecutionDetails = (execution) => {
    selectedExecution.value = execution
    detailsVisible.value = true
}

// 格式化日期
const formatDate = (dateStr) => {
    if (!dateStr) return '未知'
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

// 格式化JSON
const formatJson = (data) => {
    if (!data) return 'null'
    return JSON.stringify(data, null, 2)
}

// 分页处理
const handleSizeChange = (size) => {
    emit('size-change', size)
}

const handleCurrentChange = (page) => {
    emit('page-change', page)
}
</script>

<style scoped>
.tool-execution-details {
    margin-bottom: 24px;
}

.detail-card {
    background: var(--common-panel-background-color);
  border-radius: var(--common-radius-lg);
  overflow: hidden;
  box-shadow: var(--common-shadow-xs);
  border: 1px solid var(--common-border-color);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
  border-bottom: 1px solid var(--common-border-color);
  background: var(--common-panel-background-color);
}

.header-title {
    font-size: var(--common-font-size-title-md);
  font-weight: 600;
  color: var(--common-text-color-heavy);
    display: flex;
    align-items: center;
    gap: 8px;
}

.header-icon {
    font-size: 18px;
  color: var(--common-primary-color);
}

.filter-input {
    width: 300px;
}

.filter-input :deep(.el-input__wrapper) {
    border-radius: var(--common-radius-md);
  border: 1px solid var(--common-border-color);
}

.filter-input :deep(.el-input__wrapper:hover) {
    border-color: var(--common-primary-color);
}

.search-append-btn {
    border-radius: 0 var(--common-radius-md) var(--common-radius-md) 0;
  border: none;
}

.table-container {
    max-height: 600px;
    overflow-y: auto;
}

.detail-table {
    border-radius: 0;
}

.tool-info {
    display: flex;
    align-items: center;
}

.tool-name {
    font-weight: 600;
    color: var(--common-text-color-heavy);
}

.service-tag {
    border-radius: var(--common-radius-sm);
  font-weight: 500;
}

.module-tag {
    border-radius: var(--common-radius-sm);
  font-weight: 500;
}

.creator-name {
    font-weight: 500;
    color: var(--common-text-color);
}

.status-tag {
    border-radius: var(--common-radius-sm);
  font-weight: 600;
}

.execution-time {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-weight: 600;
    color: var(--common-text-color-heavy);
}

.created-time {
    font-size: 13px;
    color: var(--common-text-color);
}

.no-data {
    color: var(--common-text-color-lighter);
    font-style: italic;
}

.details-button {
    border-radius: var(--common-radius-md);
  font-weight: 600;
  border: none;
}

/* 对话框样式 */
.execution-dialog {
    border-radius: var(--common-radius-lg);
  overflow: hidden;
}

.execution-dialog :deep(.el-dialog__header) {
    background: var(--common-panel-background-color);
    color: var(--common-text-color-heavy);
    border-bottom: 1px solid var(--common-border-color);
}

.execution-header {
    margin-bottom: 24px;
}

.execution-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.execution-title h3 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    color: var(--common-text-color-heavy);
}

.execution-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.meta-label {
    font-weight: 600;
    color: var(--common-text-color);
}

.meta-value {
    font-weight: 500;
    color: var(--common-text-color-heavy);
}

.content-section {
    margin-bottom: 20px;
}

.content-section h4 {
    margin-top: 0;
    margin-bottom: 10px;
    color: var(--common-text-color-heavy);
    font-weight: bold;
}

.code-container {
    background: var(--common-list-background-color);
  border: 1px solid var(--common-border-color);
  border-radius: var(--common-radius-md);
  padding: 12px;
}

.code-container.error {
    background: var(--common-error-background-color);
  border-color: var(--common-error-color);
}

.code-container pre {
    margin: 0;
    padding: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    color: var(--common-text-color-heavy);
    font-size: 13px;
}

.code-container.error pre {
    color: var(--common-error-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .card-header {
        padding: 12px;
        flex-direction: column;
        gap: 12px;
        align-items: stretch;
    }

    .filter-input {
        width: 100%;
    }

    .execution-meta {
        flex-direction: column;
        gap: 10px;
    }
}
</style>
