<template>
  <el-card shadow="never" class="service-card">
    <template #header>
      <div class="card-header">
        <div class="flex items-center">
          <h3 class="text-lg font-bold">服务发布</h3>
          <el-tag v-if="!loadingServices" type="info" size="small" class="ml-2 service-count">
            {{ services.length }}
          </el-tag>
        </div>
        <div class="service-actions" v-if="!loadingServices">
          <el-button type="primary" size="small" @click="$emit('publish')">
            发布服务
          </el-button>
        </div>
      </div>
    </template>

    <div v-if="loadingServices" class="text-center py-2">
      <el-skeleton :rows="1" animated />
    </div>
    <div v-else-if="services.length === 0" class="text-center py-4">
      <el-empty description="暂无服务" :image-size="60">
        <template #description>
          <p class="text-gray-500">还没有发布服务，点击上方按钮发布</p>
        </template>
      </el-empty>
    </div>
    <div v-else class="table-container">
      <el-table :data="services" style="width: 100%" size="small" class="service-table"
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
        :max-height="tableMaxHeight">
        <el-table-column label="序号" width="50">
          <template #default="scope">
            {{ scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_public" label="公开" width="60">
          <template #default="scope">
            <el-tag :type="scope.row.is_public ? 'success' : 'warning'" size="small">
              {{ scope.row.is_public ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="服务名称" min-width="120">
          <template #default="scope">
            <el-text truncated>
              {{ scope.row.name }}
            </el-text>
          </template>
        </el-table-column>
        <el-table-column prop="sse_url" label="SSE URL" min-width="220">
          <template #default="scope">
            <div class="flex items-center">
              <el-tooltip :content="scope.row.sse_url" placement="top" :show-after="500">
                <el-input v-model="scope.row.sse_url" readonly size="small" class="flex-1 mr-1"
                  :title="scope.row.sse_url" disabled />
              </el-tooltip>
              <el-button type="primary" circle size="small" @click="copyUrl(scope.row.sse_url)" title="复制URL">
                <el-icon>
                  <DocumentCopy />
                </el-icon>
              </el-button>
              <el-button type="success" circle size="small" @click="copyAsEgovakbUrl(scope.row.sse_url)"
                title="复制为egovakb格式">
                <el-icon>
                  <Connection />
                </el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="140" />
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="scope">
            <div v-if="scope.row.can_edit">
              <el-button v-if="scope.row.status === 'running'" type="info" size="small"
                @click="$emit('stop-service', scope.row.service_uuid)">
                停止
              </el-button>
              <el-button v-else-if="scope.row.status === 'stopped'" type="success" size="small"
                @click="$emit('start-service', scope.row.service_uuid)">
                启动
              </el-button>
              <el-button v-else-if="scope.row.status === 'error'" type="warning" size="small"
                @click="$emit('start-service', scope.row.service_uuid)">
                重启
              </el-button>
              <el-button type="primary" size="small" @click="$emit('view-params', scope.row)" title="查看参数">
                参数
              </el-button>
              <el-button type="danger" size="small" @click="$emit('uninstall-service', services[0].service_uuid)">
                卸载
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { DocumentCopy, Connection } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import type { McpServiceInfo } from '@/types/marketplace';
import { ref, onMounted } from 'vue';
import { copyTextToClipboard } from '@/utils/copy';

const props = defineProps<{
  services: McpServiceInfo[];
  loadingServices: boolean;
}>();

const emit = defineEmits<{
  (e: 'publish'): void;
  (e: 'stop-service', serviceUuid: string): void;
  (e: 'start-service', serviceUuid: string): void;
  (e: 'uninstall-service', serviceUuid: string): void;
  (e: 'view-params', service: McpServiceInfo): void;
}>();

// 表格最大高度，设置为三行的高度（每行约51px，含表头总高约204px）
const tableMaxHeight = ref(144);

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'running':
      return 'success';
    case 'stopped':
      return 'warning';
    case 'error':
      return 'danger';
    default:
      return 'info';
  }
};

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中';
    case 'stopped':
      return '已停止';
    case 'error':
      return '错误';
    default:
      return status;
  }
};

// 复制URL到剪贴板
const copyUrl = (url: string) => {
  copyTextToClipboard(url);
};

// 复制为egovakb格式的URL
const copyAsEgovakbUrl = (url: string) => {
  // 创建egovakb格式的JSON
  const egovakbFormat = JSON.stringify({
    "mcp-sse": {
      "url": url,
      "transport": "sse"
    }
  }, null, 2);

  // 复制到剪贴板
  navigator.clipboard.writeText(egovakbFormat).then(() => {
    ElMessage.success('egovakb格式URL已复制到剪贴板');
  }).catch(() => {
    // 回退处理
    const textArea = document.createElement('textarea');
    textArea.value = egovakbFormat;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    ElMessage.success('egovakb格式URL已复制到剪贴板');
  });
};
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-card {
  border-radius: 16px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  transition: all 0.3s ease;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff, #f8f9ff);
}

.service-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-2px);
}

:deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(235, 235, 235, 0.6);
  background: rgba(250, 252, 255, 0.7);
}

.service-actions {
  display: flex;
  align-items: center;
}

:deep(.el-table) {
  --el-table-border-color: rgba(235, 235, 235, 0.6);
  --el-table-header-bg-color: rgba(246, 248, 250, 0.6);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: rgba(246, 248, 250, 0.6);
  font-weight: 600;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background-color: rgba(240, 247, 255, 0.6);
}

:deep(.el-table .cell) {
  padding: 8px 12px;
}

.table-container {
  position: relative;
  width: 100%;
}

.service-table {
  margin-top: 8px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background: #c0c4cc;
  border-radius: 3px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 3px;
}

:deep(.service-table .el-input__inner) {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
  background-color: #f8f9fb;
}

:deep(.service-table .el-input__wrapper) {
  box-shadow: none;
  border: 1px solid #e0e3e9;
}

:deep(.service-table .el-input__wrapper:hover) {
  border-color: #c0c4cc;
}

.service-count {
  border-radius: 12px;
  padding: 0 8px;
  font-size: 12px;
  height: 20px;
  line-height: 20px;
  background-color: #f0f2f5;
  color: #606266;
}
</style> 