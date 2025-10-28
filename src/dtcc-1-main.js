import { createApp } from 'vue'
import DTCC1App from './DTCC1App.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(DTCC1App)
installPostSession(app)
app.mount('#app')
