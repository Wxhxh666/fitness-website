import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
    watch: {
      // 忽略文件沙箱做原子写入时产生的临时目录 / 临时文件，避免监听器 EBUSY 崩溃
      ignored: (p: string) =>
        p.includes('.tmpdir') || p.endsWith('.tmp') ||
        p.includes('/node_modules/') || p.includes('/.git/'),
    },
  },
})
