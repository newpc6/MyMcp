import axios from 'axios';
import { ElMessage } from 'element-plus';
import router from '../router';
export const apiPrefix = '/api/v1/mcp'
// 创建axios实例
const api = axios.create({
    // baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // 启用跨域认证，确保发送cookie
});

// 请求拦截器
api.interceptors.request.use(
    (config) => {
        // 确保所有请求都使用withCredentials
        config.withCredentials = true;
        
        // 从localStorage获取用户信息
        const userInfoStr = localStorage.getItem('userInfo');
        // console.log('拦截器获取到的用户信息:', userInfoStr ? '有数据' : '无数据');
        
        if (userInfoStr) {
            try {
                const userInfo = JSON.parse(userInfoStr);
                // 如果有token，添加到请求头
                if (userInfo && userInfo.token) {
                    // console.log('设置Authorization头:', `Bearer ${userInfo.token.substring(0, 15)}...`);
                    // 确保headers对象存在
                    config.headers = config.headers || {};
                    config.headers['Authorization'] = `Bearer ${userInfo.token}`;
                } else {
                    console.warn('userInfo中没有找到token');
                }
            } catch (e) {
                console.error('解析用户信息失败', e);
            }
        } else {
            console.warn('localStorage中没有找到userInfo');
        }
        
        // 检查最终的请求头
        // console.log('最终请求头:', JSON.stringify(config.headers));
        // console.log('是否发送cookies:', config.withCredentials);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        console.error('API请求错误:', error);
        
        // 处理401未授权错误
        if (error.response && error.response.status === 401) {
            console.warn('收到401未授权错误');
            
            // 清除用户信息
            localStorage.removeItem('userInfo');
            
            // 显示提示消息
            ElMessage.error('会话已过期，请重新登录');
            
            // 使用 nextTick 确保在下一个事件循环中处理路由跳转
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // 检查当前路由，避免重复跳转
            if (router.currentRoute.value.name !== 'login') {
                // 使用 replace 避免产生历史记录
                await router.replace('/login');
                
                // 强制刷新页面以确保状态完全清理
                window.location.reload();
            }
        }
        return Promise.reject(error);
    }
);

// 导出API实例
export default api; 
