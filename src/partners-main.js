import { createApp } from 'vue'
import PartnersApp from './PartnersApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(PartnersApp)
installPostSession(app)
app.mount('#app')
