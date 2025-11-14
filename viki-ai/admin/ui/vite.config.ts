import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'spa-fallback',
      configureServer(server) {
        return () => {
          server.middlewares.use((req, _res, next) => {
            // Let Vite's built-in middleware handle special paths
            if (req.url?.startsWith('/@') ||
                req.url?.startsWith('/node_modules') ||
                req.url?.startsWith('/src/')) {
              return next()
            }

            // For everything else, check if file exists in public directory
            const urlPath = req.url?.split('?')[0] || '' // Remove query params
            const filePath = path.join(__dirname, 'public', urlPath)

            try {
              if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
                return next() // File exists, let Vite serve it
              }
            } catch (err) {
              // If we can't stat the file, assume it doesn't exist
            }

            // File doesn't exist, serve index.html for SPA routing
            req.url = '/index.html'
            next()
          })
        }
      }
    }
  ],
  server: {
    port: 14001,
    host: true
  },
  build: {
    outDir: 'dist'
  }
})