import { createApp } from 'vue'
import DTCC1DetailApp from './DTCC1DetailApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(DTCC1DetailApp)
installPostSession(app)
app.mount('#app')
