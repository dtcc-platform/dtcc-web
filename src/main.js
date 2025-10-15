import { createApp } from 'vue'
import App from './App.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(App)
installPostSession(app)
app.mount('#app')
