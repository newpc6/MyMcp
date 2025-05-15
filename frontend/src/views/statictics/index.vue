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
      <el-col :xs="24" :md="12" :lg="8">
        <el-card class="ranking-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">模块发布排名</span>
              <el-button type="primary" size="small" @click="refreshModuleRankings" class="refresh-button">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="fixed-height-table">
            <el-table 
              :data="moduleRankings" 
              stripe 
              style="width: 100%" 
              v-loading="loadingModules"
              class="enhanced-table"
              :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
            >
              <el-table-column label="排名" width="60" align="center">
                <template #default="scope">
                  <div class="ranking-number">{{ (moduleCurrentPage - 1) * 5 + scope.$index + 1 }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="module_name" label="模块名称" min-width="120">
                <template #default="scope">
                  <el-text class="name-text" :title="scope.row.module_name" truncated>
                    {{ scope.row.module_name }}
                  </el-text>
                </template>
              </el-table-column>
              <el-table-column prop="service_count" label="服务数量" width="100" align="center">
                <template #default="scope">
                  <el-tag size="small" type="success" effect="plain">{{ scope.row.service_count }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="user_name" label="创建者" width="100" align="center" />
            </el-table>
          </div>
          <div class="ranking-pagination">
            <el-pagination
              small
              layout="prev, pager, next"
              :total="moduleTotalItems"
              :page-size="5"
              :current-page="moduleCurrentPage"
              @current-change="handleModulePageChange"
              background
            />
          </div>
        </el-card>
      </el-col>
      
      <!-- 工具调用排名 -->
      <el-col :xs="24" :md="12" :lg="8">
        <el-card class="ranking-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">工具调用排名</span>
              <el-button type="primary" size="small" @click="refreshToolRankings" class="refresh-button">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="fixed-height-table">
            <el-table 
              :data="toolRankings" 
              stripe 
              style="width: 100%" 
              v-loading="loadingTools"
              class="enhanced-table"
              :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
            >
              <el-table-column label="排名" width="60" align="center">
                <template #default="scope">
                  <div class="ranking-number">{{ (toolCurrentPage - 1) * 5 + scope.$index + 1 }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="tool_name" label="工具名称" min-width="120">
                <template #default="scope">
                  <el-text class="name-text" :title="scope.row.tool_name" truncated>
                    {{ scope.row.tool_name }}
                  </el-text>
                </template>
              </el-table-column>
              <el-table-column prop="call_count" label="调用次数" width="100" align="center">
                <template #default="scope">
                  <el-tag size="small" type="info" effect="plain">{{ scope.row.call_count }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="成功率" width="100" align="center">
                <template #default="scope">
                  <el-progress 
                    :percentage="calculateSuccessRate(scope.row)" 
                    :status="getSuccessRateStatus(scope.row)"
                    :stroke-width="8"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="ranking-pagination">
            <el-pagination
              small
              layout="prev, pager, next"
              :total="toolTotalItems"
              :page-size="5"
              :current-page="toolCurrentPage"
              @current-change="handleToolPageChange"
              background
            />
          </div>
        </el-card>
      </el-col>

      <!-- 服务调用排名 -->
      <el-col :xs="24" :md="12" :lg="8">
        <el-card class="ranking-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">服务调用排名</span>
              <el-button type="primary" size="small" @click="refreshServiceRankings" class="refresh-button">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="fixed-height-table">
            <el-table 
              :data="serviceRankings" 
              stripe 
              style="width: 100%" 
              v-loading="loadingServices"
              class="enhanced-table"
              :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
            >
              <el-table-column label="排名" width="60" align="center">
                <template #default="scope">
                  <div class="ranking-number">{{ (serviceCurrentPage - 1) * 5 + scope.$index + 1 }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="service_name" label="服务名称" min-width="120">
                <template #default="scope">
                  <el-text class="name-text" :title="scope.row.service_name" truncated>
                    {{ scope.row.service_name }}
                  </el-text>
                </template>
              </el-table-column>
              <el-table-column prop="module_name" label="所属模块" width="120">
                <template #default="scope">
                  <el-text class="name-text" :title="scope.row.module_name" truncated>
                    {{ scope.row.module_name }}
                  </el-text>
                </template>
              </el-table-column>
              <el-table-column prop="call_count" label="调用次数" width="100" align="center">
                <template #default="scope">
                  <el-tag size="small" type="warning" effect="plain">{{ scope.row.call_count }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="成功率" width="100" align="center">
                <template #default="scope">
                  <el-progress 
                    :percentage="calculateServiceSuccessRate(scope.row)" 
                    :status="getServiceSuccessRateStatus(scope.row)"
                    :stroke-width="8"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="ranking-pagination">
            <el-pagination
              small
              layout="prev, pager, next"
              :total="serviceTotalItems"
              :page-size="5"
              :current-page="serviceCurrentPage"
              @current-change="handleServicePageChange"
              background
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 工具调用详情 -->
    <el-card class="detail-card">
      <template #header>
        <div class="card-header">
          <span class="header-title">工具调用详情</span>
          <div class="header-actions">
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
      
      <el-table 
        :data="toolExecutions.items" 
        stripe 
        style="width: 100%" 
        v-loading="loadingExecutions"
        class="enhanced-table"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="tool_name" label="工具名称" min-width="150">
          <template #default="scope">
            <el-text class="name-text" :title="scope.row.tool_name" truncated>
              {{ scope.row.tool_name }}
            </el-text>
          </template>
        </el-table-column>
        <el-table-column label="所属服务" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.service && scope.row.service.name" size="small" type="primary" effect="plain">
              <el-text class="tag-text" :title="scope.row.service.name" truncated>
                {{ scope.row.service.name }}
              </el-text>
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="所属模块" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.module && scope.row.module.name" size="small" type="success" effect="plain">
              <el-text class="tag-text" :title="scope.row.module.name" truncated>
                {{ scope.row.module.name }}
              </el-text>
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="创建者" width="120">
          <template #default="scope">
            <el-text class="name-text" :title="scope.row.creator_name || '-'" truncated>
              {{ scope.row.creator_name || '-' }}
            </el-text>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="execution_time" label="执行时间" width="120" align="right">
          <template #default="scope">
            {{ scope.row.execution_time }} ms
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="showExecutionDetails(scope.row)" class="details-button">
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
          background
        />
      </div>
    </el-card>
    
    <!-- 工具调用详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      title="工具调用详情"
      width="70%"
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
            <div v-if="selectedExecution.service && selectedExecution.service.name" class="meta-item">
              <span class="meta-label">所属服务:</span>
              <span class="meta-value">{{ selectedExecution.service.name }}</span>
            </div>
            <div v-if="selectedExecution.module && selectedExecution.module.name" class="meta-item">
              <span class="meta-label">所属模块:</span>
              <span class="meta-value">{{ selectedExecution.module.name }}</span>
            </div>
            <div v-if="selectedExecution.creator_name" class="meta-item">
              <span class="meta-label">创建者:</span>
              <span class="meta-value">{{ selectedExecution.creator_name }}</span>
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
  getServiceRankings,
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
const moduleCurrentPage = ref(1);
const moduleTotalItems = ref(0);

// 工具调用排名
const toolRankings = ref([]);
const loadingTools = ref(false);
const toolCurrentPage = ref(1);
const toolTotalItems = ref(0);

// 服务调用排名
const serviceRankings = ref([]);
const loadingServices = ref(false);
const serviceCurrentPage = ref(1);
const serviceTotalItems = ref(0);

// 工具调用详情
const toolExecutions = ref({
  items: [],
  total: 0,
  page: 1,
  size: 10,
  pages: 0
});
const loadingExecutions = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
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

// 计算服务调用成功率
const calculateServiceSuccessRate = (service) => {
  if (service.call_count === 0) return 0;
  return Math.round((service.success_count / service.call_count) * 100);
};

// 获取服务成功率状态
const getServiceSuccessRateStatus = (service) => {
  const rate = calculateServiceSuccessRate(service);
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
const loadModuleRankings = async (page = 1) => {
  loadingModules.value = true;
  try {
    const response = await getModuleRankings(5, page);
    if (response && response.code === 0) {
      moduleRankings.value = response.data.items;
      moduleTotalItems.value = response.data.total;
    }
  } catch (error) {
    console.error('获取模块排名失败', error);
    ElMessage.error('获取模块排名失败');
  } finally {
    loadingModules.value = false;
  }
};

// 获取工具调用排名
const loadToolRankings = async (page = 1) => {
  loadingTools.value = true;
  try {
    const response = await getToolRankings(5, page);
    if (response && response.code === 0) {
      toolRankings.value = response.data.items;
      toolTotalItems.value = response.data.total;
    }
  } catch (error) {
    console.error('获取工具排名失败', error);
    ElMessage.error('获取工具排名失败');
  } finally {
    loadingTools.value = false;
  }
};

// 获取服务调用排名
const loadServiceRankings = async (page = 1) => {
  loadingServices.value = true;
  try {
    const response = await getServiceRankings(5, page);
    if (response && response.code === 0) {
      serviceRankings.value = response.data.items;
      serviceTotalItems.value = response.data.total;
    }
  } catch (error) {
    console.error('获取服务排名失败', error);
    ElMessage.error('获取服务排名失败');
  } finally {
    loadingServices.value = false;
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
      refreshModuleRankings();
      refreshToolRankings();
      refreshServiceRankings();
      loadToolExecutions();
    }
  } catch (error) {
    console.error('刷新统计数据失败', error);
    ElMessage.error('刷新统计数据失败');
  }
};

// 分页处理函数
const handleModulePageChange = (page) => {
  moduleCurrentPage.value = page;
  loadModuleRankings(page);
};

const handleToolPageChange = (page) => {
  toolCurrentPage.value = page;
  loadToolRankings(page);
};

const handleServicePageChange = (page) => {
  serviceCurrentPage.value = page;
  loadServiceRankings(page);
};

// 刷新模块排名
const refreshModuleRankings = () => {
  moduleCurrentPage.value = 1;
  loadModuleRankings(1);
};

// 刷新工具排名
const refreshToolRankings = () => {
  toolCurrentPage.value = 1;
  loadToolRankings(1);
};

// 刷新服务排名
const refreshServiceRankings = () => {
  serviceCurrentPage.value = 1;
  loadServiceRankings(1);
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
  loadServiceRankings();
  loadToolExecutions();
});
</script>

<style scoped>
.statistics-page {
  padding: 20px;
  max-width: 1400px;
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
  padding: 0 5px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.filter-input {
  width: 250px;
  margin-right: 10px;
}

@media (max-width: 768px) {
  .header-actions {
    margin-top: 10px;
    width: 100%;
  }
  
  .filter-input {
    width: calc(100% - 80px);
    margin-right: 10px;
  }
}

.refresh-button {
  transition: transform 0.3s;
}

.refresh-button:hover {
  transform: rotate(90deg);
}

.ranking-number {
  display: inline-flex;
  width: 22px;
  height: 22px;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  background-color: #f0f0f0;
  color: #606266;
  font-weight: bold;
  font-size: 12px;
}

.fixed-height-table {
  height: 280px;
  overflow: hidden;
}

.ranking-pagination {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

.ranking-card {
  margin-bottom: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.ranking-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.enhanced-table {
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 15px;
}

.details-button {
  padding: 4px 16px;
}

/* 表格行悬停效果 */
.enhanced-table :deep(.el-table__row:hover) {
  background-color: #f0f7ff !important;
}

/* 表格条纹颜色调整 */
.enhanced-table :deep(.el-table__row--striped) {
  background-color: #fafafa;
}

/* 表格外边框 */
.enhanced-table :deep(.el-table) {
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

/* 表格内单元格样式 */
.enhanced-table :deep(.el-table__cell) {
  padding: 12px 0;
}

/* 排名前三样式 */
.ranking-number:nth-child(1),
.ranking-number:first-child {
  background-color: #ffd700;
  color: #fff;
}
.ranking-number:nth-child(2) {
  background-color: #c0c0c0;
  color: #fff;
}
.ranking-number:nth-child(3) {
  background-color: #cd7f32;
  color: #fff;
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

.execution-dialog {
  width: 70% !important;
}

.name-text {
  display: block;
  width: 100%;
  font-size: 14px;
}

.tag-text {
  max-width: 90px;
  display: inline-block;
}
</style> 