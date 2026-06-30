<template>
  <div class="statistics-overview">
    <div class="overview-card">
      <div class="card-header">
        <div class="header-title">
          <el-icon class="header-icon">
            <DataBoard />
          </el-icon>
          服务概览统计
        </div>
        <el-button type="primary" size="small" @click="$emit('refresh')" class="refresh-button">
          <el-icon>
            <Refresh />
          </el-icon>
          刷新
        </el-button>
      </div>

      <div class="stats-grid">
        <!-- 服务状态统计 -->
        <div class="stats-section">
          <h4 class="section-title">
            <el-icon><Monitor /></el-icon>
            服务状态
          </h4>
          <div class="stats-row">
            <div class="stats-card total">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><Promotion /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ serviceStats.total_services }}</div>
                  <div class="card-label">服务总数</div>
                </div>
              </div>
            </div>

            <div class="stats-card running">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><VideoPlay /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ serviceStats.running_services }}</div>
                  <div class="card-label">运行中</div>
                </div>
              </div>
            </div>

            <div class="stats-card stopped">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><VideoPause /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ serviceStats.stopped_services }}</div>
                  <div class="card-label">已停止</div>
                </div>
              </div>
            </div>

            <div class="stats-card error">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ serviceStats.error_services }}</div>
                  <div class="card-label">异常</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 模板统计 -->
        <div class="stats-section">
          <h4 class="section-title">
            <el-icon><Document /></el-icon>
            模板统计
          </h4>
          <div class="stats-row">
            <div class="stats-card template-groups">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><Folder /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ serviceStats.total_template_groups }}</div>
                  <div class="card-label">模板组总数</div>
                  <div class="card-today">
                    今日新增: +{{ serviceStats.today_new_template_groups }}
                  </div>
                </div>
              </div>
            </div>

            <div class="stats-card templates">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><DocumentCopy /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ serviceStats.total_templates }}</div>
                  <div class="card-label">模板总数</div>
                  <div class="card-today">
                    今日新增: +{{ serviceStats.today_new_templates }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 调用统计 -->
        <div class="stats-section">
          <h4 class="section-title">
            <el-icon><DataAnalysis /></el-icon>
            调用统计
          </h4>
          <div class="stats-row">
            <div class="stats-card service-calls">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ formatNumber(serviceStats.total_service_calls) }}</div>
                  <div class="card-label">服务调用总数</div>
                  <div class="card-today">
                    今日新增: +{{ formatNumber(serviceStats.today_new_service_calls) }}
                  </div>
                </div>
              </div>
            </div>

            <div class="stats-card tools-calls">
              <div class="card-content">
                <div class="card-icon">
                  <el-icon><Tools /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ formatNumber(serviceStats.total_tools_calls) }}</div>
                  <div class="card-label">工具调用总数</div>
                  <div class="card-today">
                    今日新增: +{{ formatNumber(serviceStats.today_new_tools_calls) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  DataBoard,
  Refresh,
  Monitor,
  Promotion,
  VideoPlay,
  VideoPause,
  Warning,
  Document,
  Folder,
  DocumentCopy,
  DataAnalysis,
  Connection,
  Tools
} from '@element-plus/icons-vue'

// 接收统计数据
defineProps({
  serviceStats: {
    type: Object,
    default: () => ({
      total_services: 0,
      running_services: 0,
      stopped_services: 0,
      error_services: 0,
      total_template_groups: 0,
      today_new_template_groups: 0,
      total_templates: 0,
      today_new_templates: 0,
      total_service_calls: 0,
      today_new_service_calls: 0,
      total_tools_calls: 0,
      today_new_tools_calls: 0
    })
  }
})

// 定义事件
defineEmits(['refresh'])

// 格式化数字（大数字使用K、M等单位）
const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped>
.statistics-overview {
  margin-bottom: 32px;
}

.overview-card {
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
  font-size: 20px;
  color: var(--common-primary-color);
}

.refresh-button {
  border-radius: var(--common-radius-md);
}



.stats-grid {
  padding: 20px;
  gap: 16px;
  display: flex;
  flex-direction: column;

}

.stats-section {
  background: var(--common-list-background-color);
  border-radius: var(--common-radius-lg);
  padding: 16px;
  border: 1px solid var(--common-border-color);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--common-text-color-heavy);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stats-card {
  background: var(--common-panel-background-color);
  border-radius: var(--common-radius-md);
  padding: 16px;
  border: 1px solid var(--common-border-color);
  transition: box-shadow 0.2s ease;
  color: var(--common-text-color);
}

.stats-card:hover {
  box-shadow: var(--common-shadow-sm);
}

.card-content {
  display: flex !important;
  flex-direction: row !important;
  align-items: center;
  gap: 16px;

}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--common-radius-md);
  background: var(--common-primary-background-color);
  color: var(--common-primary-color);
  border: 1px solid var(--zartd-primary-2);
  font-size: 24px;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--common-text-color-heavy);
  line-height: 30px;
  margin-bottom: 4px;
}

.card-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--common-text-color-light);
}

.card-today {
  font-size: 12px;
  color: var(--common-text-color-lighter);
  margin-top: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }

  .card-header {
    padding: 12px;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .stats-grid {
    padding: 12px;
  }
}
</style> 