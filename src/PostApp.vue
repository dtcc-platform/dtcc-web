<template>
  <div class="page-shell">
    <HeaderNav />
    <main class="post-main">
      <PostWizard v-if="isAuthenticated" />
      <LoginGate v-else @authenticated="handleAuthenticated" />
    </main>
    <FooterSection />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, provide, ref, watch } from 'vue'
import HeaderNav from './components/HeaderNav.vue'
import FooterSection from './components/FooterSection.vue'
import PostWizard from './components/PostWizard.vue'
import LoginGate from './components/LoginGate.vue'

const AUTH_SESSION_KEY = 'dtcc-post-session'

const session = ref({ token: '', expiresAt: 0 })
const now = ref(Date.now())
const isAuthenticated = computed(() => isSessionActive(session.value, now.value))

function handleAuthenticated(token, expiresAt = 0) {
  now.value = Date.now()
  updateSession({ token, expiresAt })
}

function updateSession({ token, expiresAt }) {
  now.value = Date.now()
  const normalized = {
    token: token || '',
    expiresAt: Number(expiresAt) || 0,
  }
  session.value = normalized
  if (typeof window !== 'undefined') {
    if (normalized.token && isSessionActive(normalized)) {
      window.sessionStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(normalized))
    } else {
      window.sessionStorage.removeItem(AUTH_SESSION_KEY)
    }
  }
}

function isSessionActive(data, timestamp = Date.now()) {
  if (!data || !data.token) return false
  const expiresAt = Number(data.expiresAt) || 0
  if (!expiresAt) return true
  return expiresAt * 1000 > timestamp
}

function clearSession() {
  now.value = Date.now()
  updateSession({ token: '', expiresAt: 0 })
}

let heartbeat = null

onMounted(() => {
  if (typeof window === 'undefined') return
  try {
    const raw = window.sessionStorage.getItem(AUTH_SESSION_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (isSessionActive(parsed, Date.now())) {
      session.value = {
        token: parsed.token,
        expiresAt: Number(parsed.expiresAt) || 0,
      }
      now.value = Date.now()
    } else {
      window.sessionStorage.removeItem(AUTH_SESSION_KEY)
    }
  } catch {
    window.sessionStorage.removeItem(AUTH_SESSION_KEY)
  }
  heartbeat = window.setInterval(() => {
    now.value = Date.now()
  }, 15000)
})

watch(isAuthenticated, (active) => {
  if (!active && session.value.token) {
    clearSession()
  }
})

onBeforeUnmount(() => {
  if (heartbeat) {
    window.clearInterval(heartbeat)
    heartbeat = null
  }
})

const authToken = computed(() => (isSessionActive(session.value, now.value) ? session.value.token : ''))

provide('postAuthSession', session)
provide('postAuthToken', authToken)
provide('postIsAuthenticated', isAuthenticated)
provide('postLogout', clearSession)
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--unnamed-color-fafafa);
}

.post-main {
  flex: 1 0 auto;
  display: flex;
  align-items: stretch;
  padding: 56px 0 80px;
}

@media (max-width: 768px) {
  .post-main {
    padding: 32px 0 64px;
  }
}
</style>
