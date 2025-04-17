// 后端API配置
export const API_CONFIG = {
    // 从环境变量获取后端地址，如果没有则使用API前缀（通过Vite代理到后端）
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    // API超时时间（毫秒）
    timeout: 30000,
    // 是否启用调试模式
    debug: import.meta.env.VITE_DEBUG === 'true',
};

// 导出配置
export default API_CONFIG; 