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
        <el-table-column label="序号" width="78">
          <template #default="scope">
            <div class="index-cell">
              {{ scope.$index + 1 }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="150" align="center">
          <template #default="scope">
            <div class="flex items-center">
              <el-tag :type="getStatusType(scope.row.status)" size="small">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            <span>
              <el-tag type="success" size="small" v-if="scope.row.is_public">
                公开
              </el-tag>
              <el-tag type="warning" size="small" v-else>
                未公开
              </el-tag>
              </span>
            </div>
          </template>
        </el-table-column>
        <!-- <el-table-column prop="is_public" label="公开" width="85">
          <template #default="scope">
            <el-tag :type="scope.row.is_public ? 'success' : 'warning'" size="small" align="center">
              {{ scope.row.is_public ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column> -->
        <el-table-column prop="auth_required" label="鉴权" width="95" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.auth_required ? 'warning' : 'info'" size="small">
              {{ scope.row.auth_required ? '启用' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="服务名称" min-width="120" align="center">
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
        <el-table-column prop="created_at" label="创建时间" width="120" />
        <el-table-column label="操作" width="310">
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
              <el-button 
                v-if="scope.row.auth_required" 
                type="warning" 
                size="small" 
                @click="$emit('manage-auth', scope.row)" 
                title="管理密钥"
              >
                密钥
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
import type { McpServiceInfo } from '../../../types/marketplace';
import { ref, onMounted } from 'vue';
import { copyTextToClipboard } from '../../../utils/copy';

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
  (e: 'manage-auth', service: McpServiceInfo): void;
}>();

// 表格最大高度，设置为三行的高度（每行约51px，含表头总高约204px）
const tableMaxHeight = ref(214);

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

<script lang="ts">
export default {
  name: 'ServicePublishCard'
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-card {
  border-radius: 20px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(235, 235, 235, 0.6);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  backdrop-filter: blur(10px);
  position: relative;
}

.service-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981, #3b82f6, #8b5cf6);
  border-radius: 20px 20px 0 0;
}

/* .service-card:hover {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12) !important;
  transform: translateY(-6px);
} */

:deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(235, 235, 235, 0.6);
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.service-actions {
  display: flex;
  align-items: center;
}

/* :deep(.el-button--primary) {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-radius: 12px;
  padding: 8px 16px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
} */

:deep(.el-table) {
  --el-table-border-color: rgba(235, 235, 235, 0.6);
  --el-table-header-bg-color: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

:deep(.el-table th) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
  font-weight: 600;
  color: #475569;
  border-bottom: 2px solid rgba(59, 130, 246, 0.1);
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(147, 197, 253, 0.05)) !important;
}

:deep(.el-table .cell) {
  padding: 12px 16px;
}

:deep(.el-table td) {
  border-bottom: 1px solid rgba(235, 235, 235, 0.4);
}

.table-container {
  position: relative;
  width: 100%;
  margin-top: 12px;
}

.service-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  border-radius: 4px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  background: #f1f5f9;
  border-radius: 4px;
}

:deep(.service-table .el-input__inner) {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #64748b;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
}

:deep(.service-table .el-input__wrapper) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.service-table .el-input__wrapper:hover) {
  border-color: #94a3b8;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

:deep(.service-table .el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.service-count {
  border-radius: 16px;
  padding: 0 10px;
  font-size: 12px;
  height: 22px;
  line-height: 22px;
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
  color: #475569;
  font-weight: 600;
  transition: all 0.3s ease;
}



/* :deep(.el-button--info) {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--info:hover) {
  background: linear-gradient(135deg, #4b5563, #374151);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
}

:deep(.el-button--success) {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--success:hover) {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

:deep(.el-button--warning) {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--warning:hover) {
  background: linear-gradient(135deg, #d97706, #b45309);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

:deep(.el-button--danger) {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--danger:hover) {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

:deep(.el-button) {
  margin: 0 2px;
  font-size: 12px;
  padding: 6px 12px;
}

:deep(.el-button.is-circle) {
  width: 28px;
  height: 28px;
  padding: 0;
  border-radius: 50%;
} */

h3 {
  color: #1e293b;
  font-weight: 700;
  margin: 0;
}

/* 空状态样式 */
:deep(.el-empty) {
  padding: 32px 20px;
  background: rgba(248, 250, 252, 0.5);
  border-radius: 16px;
  border: 2px dashed rgba(203, 213, 225, 0.8);
  margin: 16px 0;
}

:deep(.el-empty__description) {
  color: #64748b;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .service-card {
    border-radius: 16px;
  }

  :deep(.el-card__header) {
    padding: 16px 20px;
  }

  :deep(.el-table .cell) {
    padding: 10px 12px;
  }

  :deep(.el-button) {
    font-size: 11px;
    padding: 5px 10px;
  }

  h3 {
    font-size: 16px;
  }
}
</style>