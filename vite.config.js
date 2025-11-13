import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Auto-detect deployment target and set the proper base path
  // For CloudFront: DEPLOY_TARGET=cloudfront sets base to '/'
  // For GitHub Pages: Auto-detects and sets base to '/dtcc-web/'
  const isGhActions = process.env.GITHUB_ACTIONS === 'true'
  const repo = process.env.GITHUB_REPOSITORY?.split('/')?.pop() || ''
  const isCloudFront = process.env.DEPLOY_TARGET === 'cloudfront'
  const base = isCloudFront ? '/' : (isGhActions && repo ? `/${repo}/` : '/')
  return {
    plugins: [
      vue(),
      visualizer({
        filename: './dist/stats.html',
        open: false, // Set to true to auto-open after build
        gzipSize: true,
        brotliSize: true,
      }),
      // Note: Compression is handled by CloudFront for AWS deployments
      // GitHub Pages deployment uses pre-compression if needed
    ],
    base,
    build: {
      // Target modern browsers for better optimization
      target: 'es2020',
      // Enable CSS code splitting
      cssCodeSplit: true,
      // More aggressive minification
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true, // Remove console.logs in production
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.debug'], // Remove specific console methods
          passes: 2, // More aggressive compression
        },
        mangle: {
          safari10: true, // Better Safari compatibility
        },
      },
      rollupOptions: {
        input: {
          main: 'index.html',
          news: 'news/index.html',
          newsDetail: 'news/detail.html',
          events: 'events/index.html',
          eventsDetail: 'events/detail.html',
          projects: 'projects/index.html',
          projectsDetail: 'projects/detail.html',
          dtcc1: 'dtcc-1/index.html',
          dtcc1Detail: 'dtcc-1/detail.html',
          partners: 'partners/index.html',
          contact: 'contact/index.html',
          gallery: 'gallery/index.html',
          about: 'about/index.html',
          post: 'post/index.html',
        },
        output: {
          // Better chunk splitting strategy
          manualChunks(id) {
            // Put Vue in its own chunk
            if (id.includes('node_modules/vue')) {
              return 'vendor-vue'
            }
            // Put utilities in a shared chunk
            if (id.includes('/utils/')) {
              return 'utils'
            }
          },
        },
      }
    }
  }
})
