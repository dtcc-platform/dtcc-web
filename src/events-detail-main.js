import { createApp } from 'vue'
import EventsDetailApp from './EventsDetailApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(EventsDetailApp)
installPostSession(app)
app.mount('#app')
