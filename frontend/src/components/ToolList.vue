<template>
  <div class="tool-list">
    <h2>MCP工具列表</h2>
    <div v-if="loading" class="loading">
      加载中...
    </div>
    <div v-else-if="error" class="error">
      加载失败: {{ error }}
    </div>
    <div v-else>
      <div v-if="Object.keys(tools).length === 0" class="empty">
        暂无工具
      </div>
      <div v-else class="tools">
        <div v-for="(tool, name) in tools" :key="name" class="tool-item">
          <h3>{{ name }}</h3>
          <p class="description">{{ tool.doc || '暂无描述' }}</p>
          <div class="parameters">
            <h4>参数列表:</h4>
            <ul>
              <li v-for="(param, paramName) in tool.parameters" :key="paramName">
                {{ paramName }}: {{ param.type }}
              </li>
            </ul>
          </div>
          <div class="return-type">
            <strong>返回类型:</strong> {{ tool.return_type }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { toolApi, Tool } from '@/api/service';

export default defineComponent({
  name: 'ToolList',
  setup() {
    const tools = ref<Record<string, Tool>>({});
    const loading = ref(true);
    const error = ref<string | null>(null);

    const fetchTools = async () => {
      try {
        loading.value = true;
        const response = await toolApi.getTools();
        tools.value = response.data;
      } catch (err: any) {
        error.value = err.message || '未知错误';
        console.error('获取工具列表失败:', err);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchTools();
    });

    return {
      tools,
      loading,
      error
    };
  }
});
</script>

<style scoped>
.tool-list {
  padding: 20px;
}

.loading, .error, .empty {
  padding: 20px;
  text-align: center;
}

.error {
  color: red;
}

.tools {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.tool-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background-color: #f8f8f8;
}

.description {
  color: #666;
  margin: 10px 0;
}

.parameters {
  margin: 10px 0;
}

.parameters h4 {
  margin-bottom: 5px;
}

.parameters ul {
  padding-left: 20px;
}

.return-type {
  margin-top: 10px;
  color: #444;
}
</style> 