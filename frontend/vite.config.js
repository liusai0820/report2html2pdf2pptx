import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    minify: 'esbuild',
    target: 'es2015',
  },
  // 生产构建时移除所有 console 和 debugger
  esbuild: {
    drop: ['console', 'debugger'],
  },
  server: {
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8005',
        changeOrigin: true,
      },
      '/output': {
        target: 'http://localhost:8005',
        changeOrigin: true,
      },
      '/previews': {
        target: 'http://localhost:8005',
        changeOrigin: true,
      },
    },
  },
})
