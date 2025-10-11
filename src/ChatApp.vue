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
import { onMounted, ref } from 'vue'
import HeaderNav from './components/HeaderNav.vue'
import FooterSection from './components/FooterSection.vue'
import PostWizard from './components/PostWizard.vue'
import LoginGate from './components/LoginGate.vue'

const AUTH_KEY = 'dtcc-chat-auth'

const isAuthenticated = ref(false)

function handleAuthenticated() {
  isAuthenticated.value = true
  if (typeof window !== 'undefined') {
    window.sessionStorage.setItem(AUTH_KEY, 'granted')
  }
}

onMounted(() => {
  if (typeof window === 'undefined') return
  const stored = window.sessionStorage.getItem(AUTH_KEY)
  if (stored === 'granted') {
    isAuthenticated.value = true
  }
})
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
