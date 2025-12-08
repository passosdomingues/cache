/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Vite configuration with proxy setup.
 * @us US-0000 Project Configuration - Granularity: Build System
 */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
