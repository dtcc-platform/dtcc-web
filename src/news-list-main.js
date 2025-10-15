import { createApp } from 'vue'
import NewsListApp from './NewsListApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(NewsListApp)
installPostSession(app)
app.mount('#app')
