import { defineStore } from 'pinia'
import axios from 'axios'

export const useMCPStore = defineStore('mcp', {
  state: () => ({
    tools: {} as Record<string, any>,
    modules: {} as Record<string, any>,
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchTools() {
      this.loading = true
      try {
        const response = await axios.get('/api/tools')
        this.tools = response.data
        return response.data
      } catch (error) {
        console.error('Failed to fetch tools:', error)
        this.error = '获取工具列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async executeTool(name: string, params: Record<string, any>) {
      this.loading = true
      try {
        const response = await axios.post(`/api/tools/${name}`, params)
        return response.data
      } catch (error) {
        console.error('Failed to execute tool:', error)
        this.error = '执行工具失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchModules() {
      this.loading = true
      try {
        const response = await axios.get('/api/files')
        const modules: Record<string, any> = {}
        
        for (const file of response.data) {
          const contentResponse = await axios.get(`/api/files/${file.path}`)
          modules[file.path] = {
            ...file,
            content: contentResponse.data.content
          }
        }
        
        this.modules = modules
        return modules
      } catch (error) {
        console.error('Failed to fetch modules:', error)
        this.error = '获取模块列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createModule(path: string, content: string) {
      this.loading = true
      try {
        await axios.post(`/api/files/${path}`, { content })
        await this.fetchModules()
      } catch (error) {
        console.error('Failed to create module:', error)
        this.error = '创建模块失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateModule(path: string, content: string) {
      this.loading = true
      try {
        await axios.put(`/api/files/${path}`, { content })
        await this.fetchModules()
      } catch (error) {
        console.error('Failed to update module:', error)
        this.error = '更新模块失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteModule(path: string) {
      this.loading = true
      try {
        await axios.delete(`/api/files/${path}`)
        await this.fetchModules()
      } catch (error) {
        console.error('Failed to delete module:', error)
        this.error = '删除模块失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 