import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    watch: { usePolling: true },
  },
  preview: {
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: ['dentag-app-28tyr.ondigitalocean.app'],
  },
})
