import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Auto-detect GitHub Pages builds and set the proper base path
  const isGhActions = process.env.GITHUB_ACTIONS === 'true'
  const repo = process.env.GITHUB_REPOSITORY?.split('/')?.pop() || ''
  const base = isGhActions && repo ? `/${repo}/` : '/'
  return {
    plugins: [vue()],
    base,
    build: {
      rollupOptions: {
        input: {
          main: 'index.html',
          news: 'news/index.html',
          newsDetail: 'news/detail.html',
          projects: 'projects/index.html',
          projectsDetail: 'projects/detail.html',
          contact: 'contact/index.html',
          about: 'about/index.html',
        }
      }
    }
  }
})
