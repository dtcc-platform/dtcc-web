import { createApp } from 'vue'
import ProjectsApp from './ProjectsApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(ProjectsApp)
installPostSession(app)
app.mount('#app')
