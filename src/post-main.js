import { createApp } from 'vue'
import PostApp from './PostApp.vue'
import './assets/tokens.css'
import './assets/global.css'
import { installPostSession } from './utils/postSession'

const app = createApp(PostApp)
installPostSession(app)
app.mount('#app')
