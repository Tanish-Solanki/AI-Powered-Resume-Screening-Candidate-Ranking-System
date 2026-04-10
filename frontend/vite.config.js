import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Needed for docker mapping
    watch: {
      usePolling: true, // Needed for docker hot reload on Windows
    }
  }
})
