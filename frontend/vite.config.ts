import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/query': 'http://localhost:8000',
      '/checklist': 'http://localhost:8000',
      '/system-status': 'http://localhost:8000',
      '/rig-data': 'http://localhost:8000',
    }
  }
})
