import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Auto-detect GitHub Pages builds and set the proper base path
  const isGhActions = process.env.GITHUB_ACTIONS === 'true'
  const repo = process.env.GITHUB_REPOSITORY?.split('/')?.pop() || ''
  const base = isGhActions && repo ? `/${repo}/` : '/'
  return {
    plugins: [
      vue(),
      visualizer({
        filename: './dist/stats.html',
        open: false, // Set to true to auto-open after build
        gzipSize: true,
        brotliSize: true,
      }),
      // Gzip compression
      viteCompression({
        verbose: true,
        disable: false,
        threshold: 1024, // Only compress files larger than 1KB
        algorithm: 'gzip',
        ext: '.gz',
      }),
      // Brotli compression
      viteCompression({
        verbose: true,
        disable: false,
        threshold: 1024,
        algorithm: 'brotliCompress',
        ext: '.br',
      }),
    ],
    base,
    build: {
      rollupOptions: {
        input: {
          main: 'index.html',
          news: 'news/index.html',
          newsDetail: 'news/detail.html',
          events: 'events/index.html',
          eventsDetail: 'events/detail.html',
          projects: 'projects/index.html',
          projectsDetail: 'projects/detail.html',
          partners: 'partners/index.html',
          contact: 'contact/index.html',
          gallery: 'gallery/index.html',
          about: 'about/index.html',
          post: 'post/index.html',
        }
      }
    }
  }
})
