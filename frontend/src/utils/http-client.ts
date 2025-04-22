import axios from 'axios';
import { ElNotification } from 'element-plus';

// 创建axios实例
const httpClient = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
httpClient.interceptors.request.use(
  (config) => {
    // 可以在这里处理请求头等信息，例如添加token
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
httpClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    let message = '请求失败，请稍后再试';
    
    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response;
      
      if (status === 401) {
        message = '身份验证失败，请重新登录';
        // 可以在这里处理登出逻辑
      } else if (status === 403) {
        message = '没有权限访问该资源';
      } else if (status === 404) {
        message = '请求的资源不存在';
      } else if (status === 500) {
        message = '服务器内部错误';
      } else if (data && data.detail) {
        // 使用后端返回的错误消息
        message = data.detail;
      }
    } else if (error.request) {
      // 请求发出但没有收到响应
      message = '服务器无响应，请检查网络连接';
    }
    
    // 显示错误提示
    ElNotification({
      title: '错误',
      message,
      type: 'error',
    });
    
    return Promise.reject(error);
  }
);

export default httpClient; 