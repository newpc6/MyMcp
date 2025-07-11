<template>
    <el-card shadow="never" class="mb-2 action-search-card">
        <div class="action-search-container">
            <!-- 左侧搜索表单 -->
            <div class="search-form">
                <slot name="search">
                    <!-- 默认搜索表单插槽 -->
                </slot>
            </div>

            <!-- 右侧操作按钮 -->
            <div class="action-buttons">
                <slot name="actions">
                    <!-- 默认操作按钮插槽 -->
                </slot>
            </div>

        </div>
    </el-card>
</template>

<script setup lang="ts">
// 组件逻辑
</script>