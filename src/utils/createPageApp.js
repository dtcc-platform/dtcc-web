import { createApp } from 'vue'
import '../assets/tokens.css'
import '../assets/global.css'
import { installPostSession } from './postSession'

/**
 * Creates and mounts a Vue application with common setup.
 * This eliminates boilerplate code across all entry point files.
 *
 * @param {Component} rootComponent - The root Vue component to mount
 * @param {string} [selector='#app'] - The CSS selector for the mount element
 * @returns {App} The mounted Vue application instance
 */
export function createPageApp(rootComponent, selector = '#app') {
  const app = createApp(rootComponent)
  installPostSession(app)
  app.mount(selector)
  return app
}
