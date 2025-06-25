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
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
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

.stats-grid {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-section {
  background: rgba(248, 250, 252, 0.5);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(21, 101, 192, 0.08);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1565c0;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stats-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  color: white;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 2;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 24px;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.card-label {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 500;
}

.card-today {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
}

/* 服务状态卡片 */
.stats-card.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-card.running {
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
}

.stats-card.stopped {
  background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%);
}

.stats-card.error {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
}

/* 模板卡片 */
.stats-card.template-groups {
  background: linear-gradient(135deg, #03a9f4 0%, #0288d1 100%);
}

.stats-card.templates {
  background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%);
}

/* 调用卡片 */
.stats-card.service-calls {
  background: linear-gradient(135deg, #3f51b5 0%, #303f9f 100%);
}

.stats-card.tools-calls {
  background: linear-gradient(135deg, #673ab7 0%, #512da8 100%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    padding: 16px;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .stats-grid {
    padding: 16px;
  }
}
</style> 