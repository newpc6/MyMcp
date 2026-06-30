import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return;
          if (id.includes('@element-plus/icons-vue')) return 'element-plus-icons';
          if (id.includes('element-plus/es/components/')) {
            const comp = id.split('element-plus/es/components/')[1].split('/')[0];
            return comp < 'n' ? 'element-plus-comp-a' : 'element-plus-comp-b';
          }
          if (id.includes('element-plus')) return 'element-plus-core';
          if (id.includes('codemirror') || id.includes('@codemirror')) return 'codemirror';
          if (id.includes('vue') || id.includes('vue-router') || id.includes('pinia') || id.includes('@vue')) return 'vue';
        },
      },
    },
  },
  server: {
    port: 3005,
    host: '0.0.0.0',
    proxy: {
      '/api/v1/mcp': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      }
    }
  }
})