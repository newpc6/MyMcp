<template>
  <div class="service-ranking">
    <div class="ranking-card">
      <div class="card-header">
        <div class="header-title">
          <el-icon class="header-icon">
            <Monitor />
          </el-icon>
          服务调用排名
        </div>
        <el-button type="primary" size="small" @click="$emit('refresh')" class="refresh-button">
          <el-icon>
            <Refresh />
          </el-icon>
        </el-button>
      </div>

      <div class="table-container">
        <el-table :data="serviceRankings" stripe style="width: 100%" v-loading="loading" class="ranking-table"
          :header-cell-style="{ background: '#f8fafc', color: '#4a5568', fontWeight: '600' }">
          <el-table-column label="排名" width="60" align="center">
            <template #default="scope">
              <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="service_name" label="服务名称" min-width="120">
            <template #default="scope">
              <div class="service-info">
                <el-text truncated class="service-name">{{ scope.row.service_name }}</el-text>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="module_name" label="所属模块" width="120">
            <template #default="scope">
              <el-tag size="small" type="primary" effect="light" class="module-tag">
                {{ scope.row.module_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="call_count" label="调用次数" width="100" align="center">
            <template #default="scope">
              <el-tag size="small" type="warning" effect="light" class="count-tag">
                {{ scope.row.call_count }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="成功率" width="100" align="center">
            <template #default="scope">
              <div class="success-rate">
                <el-progress :percentage="calculateServiceSuccessRate(scope.row)"
                  :status="getServiceSuccessRateStatus(scope.row)" :stroke-width="6" :show-text="false" />
                <span class="rate-text">{{ calculateServiceSuccessRate(scope.row) }}%</span>
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
import { Monitor, Refresh } from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 定义Props
defineProps({
  serviceRankings: {
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
    default: 10
  },
  totalItems: {
    type: Number,
    default: 0
  }
})

// 定义事件
const emit = defineEmits(['refresh', 'size-change', 'page-change'])

// 获取排名样式类
const getRankingClass = (index) => {
  switch (index) {
    case 0:
      return 'ranking-first'
    case 1:
      return 'ranking-second'
    case 2:
      return 'ranking-third'
    default:
      return 'ranking-normal'
  }
}

// 计算服务调用成功率
const calculateServiceSuccessRate = (service) => {
  if (service.call_count === 0) return 0
  return Math.round((service.success_count / service.call_count) * 100)
}

// 获取服务成功率状态
const getServiceSuccessRateStatus = (service) => {
  const rate = calculateServiceSuccessRate(service)
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
.service-ranking {
  height: 100%;
}

.ranking-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.ranking-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
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
}

.header-icon {
  font-size: 20px;
  color: #2196f3;
}

.refresh-button {
  border-radius: 8px;
  transition: all 0.2s ease;
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  border: none;
}

.refresh-button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
  flex: 1;
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

.ranking-badge {
  display: inline-flex;
  width: 28px;
  height: 28px;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  font-weight: 700;
  font-size: 12px;
  color: white;
}

.ranking-first {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #744210;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.ranking-second {
  background: linear-gradient(135deg, #c0c0c0, #e2e8f0);
  color: #4a5568;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.3);
}

.ranking-third {
  background: linear-gradient(135deg, #cd7f32, #d69e2e);
  color: white;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.3);
}

.ranking-normal {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1565c0;
}

.service-info {
  display: flex;
  align-items: center;
}

.service-name {
  font-weight: 600;
  color: #1565c0;
}

.module-tag {
  border-radius: 12px;
  font-weight: 500;
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  color: #2e7d32;
  border: 1px solid rgba(46, 125, 50, 0.2);
}

.count-tag {
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1565c0;
  border: 1px solid rgba(21, 101, 192, 0.2);
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
  color: #1565c0;
}

.pagination-section {
  padding: 16px 24px;
  border-top: 1px solid rgba(21, 101, 192, 0.1);
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.02) 0%, rgba(25, 118, 210, 0.02) 100%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    padding: 16px;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style> 