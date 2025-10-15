import { createApp } from 'vue'
import GalleryApp from './GalleryApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(GalleryApp)
installPostSession(app)
app.mount('#app')
