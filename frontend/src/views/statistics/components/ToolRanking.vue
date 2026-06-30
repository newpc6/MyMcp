<template>
  <div class="tool-ranking">
    <div class="ranking-card">
      <div class="card-header">
        <div class="header-title">
          <el-icon class="header-icon">
            <Tools />
          </el-icon>
          工具调用排名
        </div>
        <el-button type="primary" size="small" @click="$emit('refresh')" class="refresh-button">
          <el-icon>
            <Refresh />
          </el-icon>
        </el-button>
      </div>

      <div class="table-container">
        <el-table :data="toolRankings" stripe style="width: 100%" v-loading="loading" class="ranking-table"
        :header-cell-style="{ background: 'var(--common-table-header-background-color)', color: 'var(--common-text-color)', fontWeight: '600' }">
          <el-table-column label="排名" width="60" align="center">
            <template #default="scope">
              <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="tool_name" label="工具名称" min-width="120">
            <template #default="scope">
              <div class="tool-info">
                <span class="tool-name">{{ scope.row.tool_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="call_count" label="调用次数" width="100" align="center">
            <template #default="scope">
              <el-tag size="small" type="info" effect="light" class="count-tag">
                {{ scope.row.call_count }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="成功率" width="100" align="center">
            <template #default="scope">
              <div class="success-rate">
                <el-progress :percentage="calculateSuccessRate(scope.row)" :status="getSuccessRateStatus(scope.row)"
                  :stroke-width="6" :show-text="false" />
                <span class="rate-text">{{ calculateSuccessRate(scope.row) }}%</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-section">
        <el-config-provider :locale="zhCn">
          <el-pagination size="small" :current-page="currentPage" :page-size="pageSize"
            :page-sizes="[5, 10, 15, 20]" :background="true" layout="total, sizes, prev, pager, next, jumper"
            :total="totalItems" @size-change="handleSizeChange" @current-change="handlePageChange" />
        </el-config-provider>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Tools, Refresh } from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { getRankingClass } from '@/utils/table'

// 定义Props
defineProps({
  toolRankings: {
    type: Array,
    default: () => []
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
    default: 5
  },
  totalItems: {
    type: Number,
    default: 0
  }
})

// 定义事件
const emit = defineEmits(['refresh', 'size-change', 'page-change'])

// 计算工具调用成功率
const calculateSuccessRate = (tool) => {
  if (tool.call_count === 0) return 0
  return Math.round((tool.success_count / tool.call_count) * 100)
}

// 获取成功率状态
const getSuccessRateStatus = (tool) => {
  const rate = calculateSuccessRate(tool)
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'exception'
}

// 分页处理
const handleSizeChange = (size) => {
  emit('size-change', size)
}

const handlePageChange = (page) => {
  emit('page-change', page)
}
</script>

<style scoped>
.tool-ranking {
  height: 100%;
}

.ranking-card {
  background: var(--common-panel-background-color);
  border-radius: var(--common-radius-lg);
  overflow: hidden;
  box-shadow: var(--common-shadow-xs);
  border: 1px solid var(--common-border-color);
  transition: box-shadow 0.2s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.ranking-card:hover {
  box-shadow: var(--common-shadow-sm);
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

.refresh-button {
  border-radius: 8px;
  transition: all 0.2s ease;
  border-radius: var(--common-radius-md);
  border: none;
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
  flex: 1;
}

.ranking-table {
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

.count-tag {
  font-weight: 600;
  border-radius: var(--common-radius-sm);
  color: var(--common-text-color-heavy);
}

.success-rate {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.rate-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--common-text-color-heavy);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    padding: 12px;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>
