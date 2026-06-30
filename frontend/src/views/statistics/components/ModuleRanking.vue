<template>
  <div class="module-ranking">
    <div class="ranking-card">
      <div class="card-header">
        <div class="header-title">
          <el-icon class="header-icon">
            <DataBoard />
          </el-icon>
          模块发布排名
        </div>
        <el-button type="primary" size="small" @click="$emit('refresh')" class="refresh-button">
          <el-icon>
            <Refresh />
          </el-icon>
        </el-button>
      </div>

      <div class="table-container">
        <el-table :data="moduleRankings" stripe style="width: 100%" v-loading="loading" class="ranking-table"
        :header-cell-style="{ background: 'var(--common-table-header-background-color)', color: 'var(--common-text-color)', fontWeight: '600' }">
          <el-table-column label="排名" width="60" align="center">
            <template #default="scope">
              <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="module_name" label="模块名称" min-width="120">
            <template #default="scope">
              <div class="module-info">
                <span class="module-name">{{ scope.row.module_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="service_count" label="服务数量" width="100" align="center">
            <template #default="scope">
              <el-tag size="small" type="success" effect="light" class="count-tag">
                {{ scope.row.service_count }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="user_name" label="创建者" width="100" align="center">
            <template #default="scope">
              <span class="creator-name">{{ scope.row.user_name }}</span>
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
import { DataBoard, Refresh } from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { getRankingClass } from '@/utils/table'

// 定义Props
defineProps({
  moduleRankings: {
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

// 分页处理
const handleSizeChange = (size) => {
  emit('size-change', size)
}

const handlePageChange = (page) => {
  emit('page-change', page)
}
</script>

<style scoped>
.module-ranking {
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

.module-info {
  display: flex;
  align-items: center;
}

.module-name {
  font-weight: 600;
  color: var(--common-text-color-heavy);
}

.creator-name {
  font-weight: 500;
  color: var(--common-text-color);
}

.count-tag {
  font-weight: 600;
  border-radius: var(--common-radius-sm);
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
