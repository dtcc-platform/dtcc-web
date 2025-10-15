import { createApp } from 'vue'
import NewsDetailApp from './NewsDetailApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(NewsDetailApp)
installPostSession(app)
app.mount('#app')
