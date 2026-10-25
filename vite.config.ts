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
  build: {
    // 拆 vendor：第三方库很少变动，单独成 chunk 后可以长期命中浏览器缓存，
    // 业务代码迭代时用户只需重新下载几十 KB 的 index chunk。
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (!id.includes('node_modules')) return
          // echarts / zrender 体积最大且只在两个图表组件里用到，单独拆开
          if (id.includes('echarts') || id.includes('zrender')) return 'vendor-echarts'
          if (id.includes('element-plus') || id.includes('@element-plus')) return 'vendor-element'
          // vue 运行时与路由：element-plus 依赖它，但方向单一，不会形成环
          if (id.includes('/vue/') || id.includes('/@vue/') || id.includes('vue-router')) return 'vendor-vue'
          return 'vendor'
        },
      },
    },
    // 拆完之后 element-plus 仍是 ~825KB（全量引入 + 长缓存，可接受），
    // 阈值调到 900 让构建输出回到干净状态，避免真实警告被噪音淹没。
    chunkSizeWarningLimit: 900,
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
