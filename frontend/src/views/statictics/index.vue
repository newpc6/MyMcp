<template>
  <div class="statistics-page">
    <h1 class="page-title">MCP统计数据</h1>
    
    <!-- 服务概览卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="stats-card total">
          <div class="card-content">
            <div class="card-value">{{ serviceStats.total_services }}</div>
            <div class="card-label">服务总数</div>
          </div>
          <div class="card-icon">
            <el-icon><Promotion /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="stats-card running">
          <div class="card-content">
            <div class="card-value">{{ serviceStats.running_services }}</div>
            <div class="card-label">运行中</div>
          </div>
          <div class="card-icon">
            <el-icon><VideoPlay /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="stats-card stopped">
          <div class="card-content">
            <div class="card-value">{{ serviceStats.stopped_services }}</div>
            <div class="card-label">已停止</div>
          </div>
          <div class="card-icon">
            <el-icon><VideoPause /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="stats-card error">
          <div class="card-content">
            <div class="card-value">{{ serviceStats.error_services }}</div>
            <div class="card-label">异常</div>
          </div>
          <div class="card-icon">
            <el-icon><Warning /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 排名和详情部分 -->
    <el-row :gutter="20" class="ranking-section">
      <!-- 模块发布排名 -->
      <el-col :xs="24" :md="12">
        <el-card class="ranking-card">
          <template #header>
            <div class="card-header">
              <span>模块发布排名</span>
              <el-button type="primary" size="small" link @click="refreshModuleRankings">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="moduleRankings" stripe style="width: 100%" v-loading="loadingModules">
            <el-table-column label="排名" width="70">
              <template #default="scope">
                <div class="ranking-number">{{ scope.$index + 1 }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="module_name" label="模块名称" />
            <el-table-column prop="service_count" label="服务数量" width="100">
              <template #default="scope">
                <el-tag size="small" type="success">{{ scope.row.service_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="user_name" label="创建者" width="100" />
          </el-table>
        </el-card>
      </el-col>
      
      <!-- 工具调用排名 -->
      <el-col :xs="24" :md="12">
        <el-card class="ranking-card">
          <template #header>
            <div class="card-header">
              <span>工具调用排名</span>
              <el-button type="primary" size="small" link @click="refreshToolRankings">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="toolRankings" stripe style="width: 100%" v-loading="loadingTools">
            <el-table-column label="排名" width="70">
              <template #default="scope">
                <div class="ranking-number">{{ scope.$index + 1 }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="tool_name" label="工具名称" />
            <el-table-column prop="call_count" label="调用次数" width="100">
              <template #default="scope">
                <el-tag size="small" type="info">{{ scope.row.call_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="成功率" width="100">
              <template #default="scope">
                <el-progress 
                  :percentage="calculateSuccessRate(scope.row)" 
                  :status="getSuccessRateStatus(scope.row)"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 工具调用详情 -->
    <el-card class="detail-card">
      <template #header>
        <div class="card-header">
          <span>工具调用详情</span>
          <div>
            <el-input
              v-model="toolFilter"
              placeholder="按工具名筛选"
              clearable
              class="filter-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #append>
                <el-button @click="loadToolExecutions(1)">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-button type="primary" size="default" @click="refreshAllStatistics">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="toolExecutions.items" stripe style="width: 100%" v-loading="loadingExecutions">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="tool_name" label="工具名称" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="execution_time" label="执行时间" width="120">
          <template #default="scope">
            {{ scope.row.execution_time }} ms
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="primary" size="small" link @click="showExecutionDetails(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="toolExecutions.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 工具调用详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      title="工具调用详情"
      width="60%"
      class="execution-dialog"
    >
      <template v-if="selectedExecution">
        <div class="execution-header">
          <div class="execution-title">
            <h3>{{ selectedExecution.tool_name }}</h3>
            <el-tag :type="selectedExecution.status === 'success' ? 'success' : 'danger'">
              {{ selectedExecution.status }}
            </el-tag>
          </div>
          <div class="execution-meta">
            <div class="meta-item">
              <span class="meta-label">执行时间:</span>
              <span class="meta-value">{{ selectedExecution.execution_time }} ms</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">创建时间:</span>
              <span class="meta-value">{{ formatDate(selectedExecution.created_at) }}</span>
            </div>
          </div>
        </div>
        
        <el-divider />
        
        <div class="execution-content">
          <div class="content-section">
            <h4>描述</h4>
            <p>{{ selectedExecution.description }}</p>
          </div>
          
          <div class="content-section">
            <h4>参数</h4>
            <el-card shadow="never" class="code-card">
              <pre>{{ formatJson(selectedExecution.parameters) }}</pre>
            </el-card>
          </div>
          
          <div class="content-section">
            <h4>结果</h4>
            <el-card shadow="never" class="code-card">
              <pre>{{ formatJson(selectedExecution.result) }}</pre>
            </el-card>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElNotification } from 'element-plus';
import { 
  Promotion, 
  VideoPlay, 
  VideoPause, 
  Warning, 
  Refresh, 
  Search 
} from '@element-plus/icons-vue';
import { 
  getServiceStats, 
  getModuleRankings, 
  getToolRankings, 
  getToolExecutions, 
  refreshStatistics
} from '../../api/statistics';

// 统计数据
const serviceStats = ref({
  total_services: 0,
  running_services: 0,
  stopped_services: 0,
  error_services: 0,
  updated_at: null
});

// 模块发布排名
const moduleRankings = ref([]);
const loadingModules = ref(false);

// 工具调用排名
const toolRankings = ref([]);
const loadingTools = ref(false);

// 工具调用详情
const toolExecutions = ref({
  items: [],
  total: 0,
  page: 1,
  per_page: 20,
  pages: 0
});
const loadingExecutions = ref(false);
const currentPage = ref(1);
const pageSize = ref(20);
const toolFilter = ref('');

// 详情对话框
const detailsVisible = ref(false);
const selectedExecution = ref(null);

// 计算工具调用成功率
const calculateSuccessRate = (tool) => {
  if (tool.call_count === 0) return 0;
  return Math.round((tool.success_count / tool.call_count) * 100);
};

// 获取成功率状态
const getSuccessRateStatus = (tool) => {
  const rate = calculateSuccessRate(tool);
  if (rate >= 90) return 'success';
  if (rate >= 70) return 'warning';
  return 'exception';
};

// 获取服务统计数据
const loadServiceStats = async () => {
  try {
    const response = await getServiceStats();
    if (response && response.code === 0) {
      serviceStats.value = response.data;
    }
  } catch (error) {
    console.error('获取服务统计数据失败', error);
    ElMessage.error('获取服务统计数据失败');
  }
};

// 获取模块发布排名
const loadModuleRankings = async () => {
  loadingModules.value = true;
  try {
    const response = await getModuleRankings();
    if (response && response.code === 0) {
      moduleRankings.value = response.data;
    }
  } catch (error) {
    console.error('获取模块排名失败', error);
    ElMessage.error('获取模块排名失败');
  } finally {
    loadingModules.value = false;
  }
};

// 获取工具调用排名
const loadToolRankings = async () => {
  loadingTools.value = true;
  try {
    const response = await getToolRankings();
    if (response && response.code === 0) {
      toolRankings.value = response.data;
    }
  } catch (error) {
    console.error('获取工具排名失败', error);
    ElMessage.error('获取工具排名失败');
  } finally {
    loadingTools.value = false;
  }
};

// 获取工具调用详情
const loadToolExecutions = async (page) => {
  if (page) currentPage.value = page;
  loadingExecutions.value = true;
  
  try {
    const response = await getToolExecutions(
      currentPage.value,
      pageSize.value,
      toolFilter.value || undefined
    );
    
    if (response && response.code === 0) {
      toolExecutions.value = response.data;
    }
  } catch (error) {
    console.error('获取工具调用详情失败', error);
    ElMessage.error('获取工具调用详情失败');
  } finally {
    loadingExecutions.value = false;
  }
};

// 刷新统计数据
const refreshAllStatistics = async () => {
  try {
    const response = await refreshStatistics();
    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: '统计数据已刷新',
        type: 'success'
      });
      
      // 重新加载所有数据
      loadServiceStats();
      loadModuleRankings();
      loadToolRankings();
      loadToolExecutions();
    }
  } catch (error) {
    console.error('刷新统计数据失败', error);
    ElMessage.error('刷新统计数据失败');
  }
};

// 刷新模块排名
const refreshModuleRankings = () => {
  loadModuleRankings();
};

// 刷新工具排名
const refreshToolRankings = () => {
  loadToolRankings();
};

// 刷新工具调用
const refreshToolExecutions = () => {
  loadToolExecutions(1);
};

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size;
  loadToolExecutions(1);
};

const handleCurrentChange = (page) => {
  loadToolExecutions(page);
};

// 显示调用详情
const showExecutionDetails = (execution) => {
  selectedExecution.value = execution;
  detailsVisible.value = true;
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 格式化JSON
const formatJson = (data) => {
  if (!data) return 'null';
  return JSON.stringify(data, null, 2);
};

// 页面加载时获取数据
onMounted(() => {
  loadServiceStats();
  loadModuleRankings();
  loadToolRankings();
  loadToolExecutions();
});
</script>

<style scoped>
.statistics-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #303133;
}

.stats-cards {
  margin-bottom: 24px;
}

.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 10px 20px;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

.card-content {
  z-index: 1;
}

.card-value {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 5px;
  color: #ffffff;
}

.card-label {
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.card-icon {
  font-size: 40px;
  color: rgba(255, 255, 255, 0.3);
}

.stats-card.total {
  background: linear-gradient(135deg, #409eff, #3a8ee6);
}

.stats-card.running {
  background: linear-gradient(135deg, #67c23a, #52a930);
}

.stats-card.stopped {
  background: linear-gradient(135deg, #909399, #707278);
}

.stats-card.error {
  background: linear-gradient(135deg, #f56c6c, #e04141);
}

.ranking-section {
  margin-bottom: 24px;
}

.ranking-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ranking-number {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  border-radius: 50%;
  background-color: #f0f0f0;
  color: #606266;
  font-weight: bold;
}

.filter-input {
  width: 250px;
  margin-right: 10px;
  display: inline-block;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.execution-header {
  margin-bottom: 20px;
}

.execution-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.execution-title h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.execution-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-label {
  font-weight: bold;
  margin-right: 5px;
  color: #606266;
}

.content-section {
  margin-bottom: 20px;
}

.content-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #303133;
}

.code-card {
  background-color: #f8f8f8;
}

.code-card pre {
  margin: 0;
  padding: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  color: #333;
}

/* 适配中小屏幕 */
@media (max-width: 768px) {
  .filter-input {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .execution-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .execution-dialog {
    width: 90% !important;
  }
}
</style> 