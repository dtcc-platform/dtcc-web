<template>
  <div class="page-shell">
    <HeaderNav />
    <main class="chat-main">
      <PostWizard v-if="isAuthenticated" />
      <LoginGate v-else @authenticated="handleAuthenticated" />
    </main>
    <FooterSection />
  </div>
</template>

<script setup>
import { onMounted, provide, ref } from 'vue'
import HeaderNav from './components/HeaderNav.vue'
import FooterSection from './components/FooterSection.vue'
import PostWizard from './components/PostWizard.vue'
import LoginGate from './components/LoginGate.vue'

const AUTH_TOKEN_KEY = 'dtcc-chat-token'

const isAuthenticated = ref(false)
const authToken = ref('')

function handleAuthenticated(token) {
  isAuthenticated.value = true
  authToken.value = token
  if (typeof window !== 'undefined') {
    window.sessionStorage.setItem(AUTH_TOKEN_KEY, token)
  }
}

onMounted(() => {
  if (typeof window === 'undefined') return
  const stored = window.sessionStorage.getItem(AUTH_TOKEN_KEY)
  if (stored) {
    isAuthenticated.value = true
    authToken.value = stored
  }
})

provide('chatAuthToken', authToken)
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--unnamed-color-fafafa);
}

.chat-main {
  flex: 1 0 auto;
  display: flex;
  align-items: stretch;
  padding: 56px 0 80px;
}

@media (max-width: 768px) {
  .chat-main {
    padding: 32px 0 64px;
  }
}
</style>
