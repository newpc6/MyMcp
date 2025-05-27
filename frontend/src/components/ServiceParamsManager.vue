<template>
  <div class="service-params-manager">
    <div v-if="!configParams || Object.keys(configParams).length === 0" class="text-center py-4">
      <el-empty description="此服务没有配置参数" :image-size="60" />
    </div>
    <div v-else>
      <el-form ref="formRef" :model="form" label-width="120px" label-position="top">
        <div v-for="(value, key) in configParams" :key="key" class="mb-4">
          <el-form-item :label="getParamDisplay(key)" label-position="left">
            <!-- 显示参数描述 -->
            <div v-if="getParamDescription(key)" class="text-sm text-gray-500 mb-2">
              {{ getParamDescription(key) }}
            </div>
            
            <!-- 根据schema类型渲染不同的输入组件 -->
            <div v-if="getParamType(key) === 'integer'">
              <el-input-number 
                v-model="form[key]" 
                :placeholder="getParamPlaceholder(key)"
                :disabled="readonly"
                @change="handleFormChange"
              />
            </div>
            <div v-else-if="getParamType(key) === 'boolean'">
              <el-switch 
                v-model="form[key]" 
                :disabled="readonly"
                @change="handleFormChange"
              />
            </div>
            <div v-else-if="getParamType(key) === 'password'">
              <el-input 
                v-model="form[key]" 
                type="password" 
                show-password 
                :placeholder="getParamPlaceholder(key)"
                :disabled="readonly"
                @input="handleFormChange"
              />
            </div>
            <div v-else>
              <el-input 
                v-model="form[key]" 
                :placeholder="getParamPlaceholder(key)"
                :disabled="readonly"
                @input="handleFormChange"
              />
            </div>
          </el-form-item>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

interface ConfigSchema {
  [key: string]: {
    type?: string;
    title?: string;
    description?: string;
    placeholder?: string;
    required?: boolean;
  };
}

const props = defineProps<{
  configParams: Record<string, any>;
  configSchema?: ConfigSchema;
  readonly?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:configParams', value: Record<string, any>): void;
}>();

const formRef = ref();
const form = ref<Record<string, any>>({});

// 使用防抖来避免频繁更新
let updateTimer: ReturnType<typeof setTimeout> | null = null;

// 处理表单变化
const handleFormChange = () => {
  if (updateTimer) {
    clearTimeout(updateTimer);
  }
  updateTimer = setTimeout(() => {
    emit('update:configParams', { ...form.value });
  }, 100);
};

// 监听配置参数变化
watch(() => props.configParams, (newParams) => {
  if (newParams) {
    // 使用JSON比较来避免不必要的更新
    const currentFormStr = JSON.stringify(form.value);
    const newParamsStr = JSON.stringify(newParams);
    if (currentFormStr !== newParamsStr) {
      form.value = { ...newParams };
    }
  }
}, { immediate: true, deep: true });

// 获取参数显示名称
const getParamDisplay = (key: string): string => {
  if (!props.configSchema) return key;

  const schema = props.configSchema[key];
  if (schema && schema.title) {
    return schema.title;
  }
  return key;
};

// 获取参数描述
const getParamDescription = (key: string): string => {
  if (!props.configSchema) return '';

  const schema = props.configSchema[key];
  if (schema && schema.description) {
    return schema.description;
  }
  return '';
};

// 获取参数类型
const getParamType = (key: string): string => {
  if (!props.configSchema) return 'string';

  const schema = props.configSchema[key];
  if (schema && schema.type) {
    return schema.type;
  }
  return 'string';
};

// 获取参数占位符
const getParamPlaceholder = (key: string): string => {
  if (!props.configSchema) return '';

  const schema = props.configSchema[key];
  if (schema && schema.placeholder) {
    return schema.placeholder;
  }
  return '';
};

// 验证表单
const validate = async () => {
  if (!formRef.value) return true;
  try {
    await formRef.value.validate();
    return true;
  } catch (error) {
    return false;
  }
};

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  if (props.configParams) {
    form.value = { ...props.configParams };
  }
};

// 暴露方法给父组件
defineExpose({
  validate,
  resetForm
});
</script>

<style scoped>
.service-params-manager {
  width: 100%;
}

.mb-4 {
  margin-bottom: 16px;
}

.text-sm {
  font-size: 14px;
}

.text-gray-500 {
  color: #909399;
}

.mb-2 {
  margin-bottom: 8px;
}

.py-4 {
  padding-top: 16px;
  padding-bottom: 16px;
}

.text-center {
  text-align: center;
}
</style> 