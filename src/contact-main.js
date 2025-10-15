import { createApp } from 'vue'
import ContactApp from './ContactApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(ContactApp)
installPostSession(app)
app.mount('#app')
