<template>
  <div class="statistics-container">    
    <!-- 服务概览卡片 -->
    <div class="stats-overview">
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
        <div class="card-decoration"></div>
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
        <div class="card-decoration"></div>
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
        <div class="card-decoration"></div>
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
        <div class="card-decoration"></div>
      </div>
    </div>
    
    <!-- 排名和详情部分 -->
    <div class="ranking-grid">
      <!-- 模块发布排名 -->
      <div class="ranking-card">
        <div class="card-header">
          <div class="header-title">
            <el-icon class="header-icon"><DataBoard /></el-icon>
            模块发布排名
          </div>
          <el-button 
            type="primary" 
            size="small" 
            @click="refreshModuleRankings" 
            class="refresh-button"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        
        <div class="table-container">
          <el-table 
            :data="moduleRankings" 
            stripe 
            style="width: 100%" 
            v-loading="loadingModules"
            class="ranking-table"
            :header-cell-style="{ background: '#f8fafc', color: '#4a5568', fontWeight: '600' }"
          >
            <el-table-column label="排名" width="60" align="center">
              <template #default="scope">
                <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                  {{ (moduleCurrentPage - 1) * modulePageSize + scope.$index + 1 }}
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
            <el-pagination
              size="small"
              :current-page="moduleCurrentPage"
              :page-size="modulePageSize"
              :page-sizes="[5, 10, 15, 20]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="moduleTotalItems"
              @size-change="handleModuleSizeChange"
              @current-change="handleModulePageChange"
            />
          </el-config-provider>
        </div>
      </div>
      
      <!-- 工具调用排名 -->
      <div class="ranking-card">
        <div class="card-header">
          <div class="header-title">
            <el-icon class="header-icon"><Tools /></el-icon>
            工具调用排名
          </div>
          <el-button 
            type="primary" 
            size="small" 
            @click="refreshToolRankings" 
            class="refresh-button"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        
        <div class="table-container">
          <el-table 
            :data="toolRankings" 
            stripe 
            style="width: 100%" 
            v-loading="loadingTools"
            class="ranking-table"
            :header-cell-style="{ background: '#f8fafc', color: '#4a5568', fontWeight: '600' }"
          >
            <el-table-column label="排名" width="60" align="center">
              <template #default="scope">
                <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                  {{ (toolCurrentPage - 1) * toolPageSize + scope.$index + 1 }}
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
                  <el-progress 
                    :percentage="calculateSuccessRate(scope.row)" 
                    :status="getSuccessRateStatus(scope.row)"
                    :stroke-width="6"
                    :show-text="false"
                  />
                  <span class="rate-text">{{ calculateSuccessRate(scope.row) }}%</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="pagination-section">
          <el-config-provider :locale="zhCn">
            <el-pagination
              size="small"
              :current-page="toolCurrentPage"
              :page-size="toolPageSize"
              :page-sizes="[5, 10, 15, 20]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="toolTotalItems"
              @size-change="handleToolSizeChange"
              @current-change="handleToolPageChange"
            />
          </el-config-provider>
        </div>
      </div>

      <!-- 服务调用排名 -->
      <div class="ranking-card">
        <div class="card-header">
          <div class="header-title">
            <el-icon class="header-icon"><Monitor /></el-icon>
            服务调用排名
          </div>
          <el-button 
            type="primary" 
            size="small" 
            @click="refreshServiceRankings" 
            class="refresh-button"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        
        <div class="table-container">
          <el-table 
            :data="serviceRankings" 
            stripe 
            style="width: 100%" 
            v-loading="loadingServices"
            class="ranking-table"
            :header-cell-style="{ background: '#f8fafc', color: '#4a5568', fontWeight: '600' }"
          >
            <el-table-column label="排名" width="60" align="center">
              <template #default="scope">
                <div class="ranking-badge" :class="getRankingClass(scope.$index)">
                  {{ (serviceCurrentPage - 1) * servicePageSize + scope.$index + 1 }}
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
                  <el-progress 
                    :percentage="calculateServiceSuccessRate(scope.row)" 
                    :status="getServiceSuccessRateStatus(scope.row)"
                    :stroke-width="6"
                    :show-text="false"
                  />
                  <span class="rate-text">{{ calculateServiceSuccessRate(scope.row) }}%</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="pagination-section">
          <el-config-provider :locale="zhCn">
            <el-pagination
              size="small"
              :current-page="serviceCurrentPage"
              :page-size="servicePageSize"
              :page-sizes="[5, 10, 15, 20]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="serviceTotalItems"
              @size-change="handleServiceSizeChange"
              @current-change="handleServicePageChange"
            />
          </el-config-provider>
        </div>
      </div>
    </div>
    
    <!-- 工具调用详情 -->
    <div class="detail-section">
      <div class="detail-card">
        <div class="card-header">
          <div class="header-title">
            <el-icon class="header-icon"><DataAnalysis /></el-icon>
            工具调用详情
          </div>
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
                <el-button @click="loadToolExecutions(1)" class="search-append-btn">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
        
        <div class="table-container">
          <el-table 
            :data="toolExecutions.items" 
            stripe 
            style="width: 100%" 
            v-loading="loadingExecutions"
            class="detail-table"
            :header-cell-style="{ background: '#f8fafc', color: '#4a5568', fontWeight: '600' }"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="tool_name" label="工具名称" min-width="150">
              <template #default="scope">
                <div class="tool-info">
                  <span class="tool-name">{{ scope.row.tool_name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="所属服务" width="120">
              <template #default="scope">
                <el-tag 
                  v-if="scope.row.service && scope.row.service.name" 
                  size="small" 
                  type="primary" 
                  effect="light"
                  class="service-tag"
                >
                  {{ scope.row.service.name }}
                </el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <el-table-column label="所属模块" width="120">
              <template #default="scope">
                <el-tag 
                  v-if="scope.row.module && scope.row.module.name" 
                  size="small" 
                  type="success" 
                  effect="light"
                  class="module-tag"
                >
                  {{ scope.row.module.name }}
                </el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <el-table-column label="创建者" width="120">
              <template #default="scope">
                <span class="creator-name">{{ scope.row.creator_name || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.status === 'success' ? 'success' : 'danger'" 
                  size="small"
                  effect="light"
                  class="status-tag"
                >
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="execution_time" label="执行时间" width="120" align="right">
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
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="showExecutionDetails(scope.row)" 
                  class="details-button"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="pagination-section">
          <el-config-provider :locale="zhCn">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :background="true"
              layout="total, sizes, prev, pager, next, jumper"
              :total="toolExecutions.total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </el-config-provider>
        </div>
      </div>
    </div>
    
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
            <el-tag 
              :type="selectedExecution.status === 'success' ? 'success' : 'danger'"
              effect="light"
            >
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
            <div class="code-container">
              <pre>{{ formatJson(selectedExecution.parameters) }}</pre>
            </div>
          </div>
          
          <div class="content-section">
            <h4>结果</h4>
            <div class="code-container">
              <pre>{{ formatJson(selectedExecution.result) }}</pre>
            </div>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElNotification } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { 
  Promotion, 
  VideoPlay, 
  VideoPause, 
  Warning, 
  Refresh, 
  Search,
  DataBoard,
  Tools,
  Monitor,
  DataAnalysis
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
const modulePageSize = ref(5);
const moduleTotalItems = ref(0);

// 工具调用排名
const toolRankings = ref([]);
const loadingTools = ref(false);
const toolCurrentPage = ref(1);
const toolPageSize = ref(5);
const toolTotalItems = ref(0);

// 服务调用排名
const serviceRankings = ref([]);
const loadingServices = ref(false);
const serviceCurrentPage = ref(1);
const servicePageSize = ref(5);
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
    const response = await getModuleRankings(modulePageSize.value, page);
    if (response && response.code === 0) {
      moduleRankings.value = response.data.items;
      console.log('moduel total', response.data.total)
      moduleTotalItems.value = response.data.total;
      moduleCurrentPage.value = response.data.page || page;
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
    const response = await getToolRankings(toolPageSize.value, page);
    if (response && response.code === 0) {
      toolRankings.value = response.data.items;
      toolTotalItems.value = response.data.total;
      toolCurrentPage.value = response.data.page || page;
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
    const response = await getServiceRankings(servicePageSize.value, page);
    if (response && response.code === 0) {
      serviceRankings.value = response.data.items;
      serviceTotalItems.value = response.data.total;
      serviceCurrentPage.value = response.data.page || page;
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
      currentPage.value = response.data.page || currentPage.value;
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

// 模块排名分页处理函数
const handleModulePageChange = (page) => {
  moduleCurrentPage.value = page;
  loadModuleRankings(page);
};

const handleModuleSizeChange = (size) => {
  modulePageSize.value = size;
  moduleCurrentPage.value = 1;
  loadModuleRankings(1);
};

// 工具排名分页处理函数
const handleToolPageChange = (page) => {
  toolCurrentPage.value = page;
  loadToolRankings(page);
};

const handleToolSizeChange = (size) => {
  toolPageSize.value = size;
  toolCurrentPage.value = 1;
  loadToolRankings(1);
};

// 服务排名分页处理函数
const handleServicePageChange = (page) => {
  serviceCurrentPage.value = page;
  loadServiceRankings(page);
};

const handleServiceSizeChange = (size) => {
  servicePageSize.value = size;
  serviceCurrentPage.value = 1;
  loadServiceRankings(1);
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

// 工具调用详情分页处理
const handleSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1;
  loadToolExecutions(1);
};

const handleCurrentChange = (page) => {
  currentPage.value = page;
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

// 获取排名样式类名
const getRankingClass = (index) => {
  if (index === 0) return 'ranking-first';
  if (index === 1) return 'ranking-second';
  if (index === 2) return 'ranking-third';
  return 'ranking-normal';
};
</script>

<style scoped>
.statistics-container {
  padding: 24px;
  /* max-width: 1440px; */
  margin: 0 auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 32px;
  flex-wrap: wrap;
}

.title-section {
  flex: 1;
  min-width: 300px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-icon {
  font-size: 28px;
  color: #667eea;
}

.page-subtitle {
  font-size: 16px;
  color: #718096;
  margin: 0;
  font-weight: 400;
}

.header-actions {
  display: flex;
  align-items: center;
}

.refresh-btn {
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.stats-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 20px;
  z-index: 2;
  position: relative;
}

.card-icon {
  font-size: 48px;
  padding: 16px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 4px;
  line-height: 1;
}

.card-label {
  font-size: 16px;
  font-weight: 500;
  opacity: 0.8;
}

.stats-card.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stats-card.total .card-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stats-card.running {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

.stats-card.running .card-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stats-card.stopped {
  background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
  color: white;
}

.stats-card.stopped .card-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stats-card.error {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
  color: white;
}

.stats-card.error .card-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.ranking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.ranking-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.ranking-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 20px;
  color: #667eea;
}

.refresh-button {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.refresh-button:hover {
  transform: scale(1.05);
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
}

.ranking-table,
.detail-table {
  border-radius: 0;
}

.ranking-table :deep(.el-table__row:hover),
.detail-table :deep(.el-table__row:hover) {
  background-color: rgba(102, 126, 234, 0.05) !important;
}

.ranking-table :deep(.el-table__row--striped),
.detail-table :deep(.el-table__row--striped) {
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
  background: linear-gradient(135deg, #e2e8f0, #cbd5e0);
  color: #4a5568;
}

.module-info,
.tool-info,
.service-info {
  display: flex;
  align-items: center;
}

.module-name,
.tool-name,
.service-name {
  font-weight: 600;
  color: #2d3748;
}

.creator-name {
  font-weight: 500;
  color: #4a5568;
}

.count-tag {
  font-weight: 600;
  border-radius: 12px;
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
  color: #4a5568;
}

.module-tag,
.service-tag {
  border-radius: 12px;
  font-weight: 500;
}

.status-tag {
  border-radius: 12px;
  font-weight: 600;
}

.execution-time {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-weight: 600;
  color: #4a5568;
}

.created-time {
  font-size: 13px;
  color: #718096;
}

.no-data {
  color: #a0aec0;
  font-style: italic;
}

.details-button {
  border-radius: 8px;
  font-weight: 600;
}

.pagination-section {
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(248, 250, 252, 0.5);
}

.detail-section {
  margin-bottom: 24px;
}

.detail-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.filter-input {
  width: 300px;
}

.search-append-btn {
  border-radius: 0 8px 8px 0;
}

.execution-dialog {
  border-radius: 20px;
  overflow: hidden;
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
  color: #2d3748;
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
  color: #718096;
}

.meta-value {
  font-weight: 500;
  color: #2d3748;
}

.content-section {
  margin-bottom: 20px;
}

.content-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #303133;
  font-weight: bold;
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