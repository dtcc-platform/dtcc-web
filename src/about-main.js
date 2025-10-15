import { createApp } from 'vue'
import AboutApp from './AboutApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(AboutApp)
installPostSession(app)
app.mount('#app')
