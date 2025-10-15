import { createApp } from 'vue'
import NewsApp from './NewsApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(NewsApp)
installPostSession(app)
app.mount('#app')
