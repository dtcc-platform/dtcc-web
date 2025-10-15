import { createApp } from 'vue'
import ProjectsDetailApp from './ProjectsDetailApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(ProjectsDetailApp)
installPostSession(app)
app.mount('#app')
