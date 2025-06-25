import api, { apiPrefix } from './index'

// 定时任务接口
export interface ScheduledTask {
  id: string
  name: string
  description: string
  category: string
  interval: string
  next_run: string
  status: string
  enabled: boolean
}

// 系统信息接口
export const getSystemInfo = () => {
  return api.get(`${apiPrefix}/system/info`)
}

// 获取已安装的Python包列表
export const getInstalledPackages = () => {
  return api.get(`${apiPrefix}/system/python/packages`)
}

// 安装Python包
export const installPackage = (data: {
  package_name: string
  version?: string
}) => {
  return api.post(`${apiPrefix}/system/python/install`, data)
}

// 升级Python包
export const upgradePackage = (data: {
  package_name: string
}) => {
  return api.post(`${apiPrefix}/system/python/upgrade`, data)
}

// 卸载Python包
export const uninstallPackage = (packageName: string) => {
  return api.delete(`${apiPrefix}/system/python/uninstall/${packageName}`)
}

// 获取系统服务状态
export const getServiceStatus = () => {
  return api.get(`${apiPrefix}/system/services/status`)
}

// 重启服务
export const restartService = (serviceName: string) => {
  return api.post(`${apiPrefix}/system/services/${serviceName}/restart`)
}

// 停止服务
export const stopService = (serviceName: string) => {
  return api.post(`${apiPrefix}/system/services/${serviceName}/stop`)
}

// 启动服务
export const startService = (serviceName: string) => {
  return api.post(`${apiPrefix}/system/services/${serviceName}/start`)
}

// 获取系统日志
export const getSystemLogs = (params?: {
  level?: string
  limit?: number
  offset?: number
}) => {
  return api.get(`${apiPrefix}/system/logs`, { params })
}

// 清空系统日志
export const clearSystemLogs = () => {
  return api.delete(`${apiPrefix}/system/logs`)
}

// 获取定时任务列表
export const getScheduledTasks = () => {
  return api.get(`${apiPrefix}/system/scheduled-tasks`)
}

// 手动执行定时任务
export const executeScheduledTask = (taskName: string) => {
  return api.post(`${apiPrefix}/system/scheduled-tasks/execute`, {
    task_name: taskName
  })
} 