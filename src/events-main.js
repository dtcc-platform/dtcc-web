import { createApp } from 'vue'
import EventsApp from './EventsApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(EventsApp)
installPostSession(app)
app.mount('#app')
