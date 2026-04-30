import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/static/',
  build: {
    outDir: '../static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/options': 'http://localhost:8000',
      '/search': 'http://localhost:8000',
      '/kwargs': 'http://localhost:8000',
    },
  },
})
