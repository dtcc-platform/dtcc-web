import { computed, ref } from 'vue'

const AUTH_SESSION_KEY = 'dtcc-post-session'

const session = ref({ token: '', expiresAt: 0 })
const now = ref(Date.now())
let initialized = false
let heartbeatId = null

function isSessionActive(data, timestamp = Date.now()) {
  if (!data || !data.token) return false
  const expiresAt = Number(data.expiresAt) || 0
  if (!expiresAt) return true
  return expiresAt * 1000 > timestamp
}

function applySession(next, { persist } = { persist: true }) {
  const normalized = {
    token: next?.token || '',
    expiresAt: Number(next?.expiresAt) || 0,
  }
  session.value = normalized

  if (typeof window === 'undefined' || persist === false) return

  if (normalized.token && isSessionActive(normalized, Date.now())) {
    try {
      window.sessionStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(normalized))
    } catch (_) {
      // ignore quota/storage errors
    }
  } else {
    window.sessionStorage.removeItem(AUTH_SESSION_KEY)
  }
}

function loadFromStorage() {
  if (typeof window === 'undefined') return
  try {
    const raw = window.sessionStorage.getItem(AUTH_SESSION_KEY)
    if (!raw) {
      applySession({ token: '', expiresAt: 0 }, { persist: false })
      return
    }
    const parsed = JSON.parse(raw)
    if (isSessionActive(parsed, Date.now())) {
      applySession(
        { token: parsed.token || '', expiresAt: Number(parsed.expiresAt) || 0 },
        { persist: false }
      )
    } else {
      window.sessionStorage.removeItem(AUTH_SESSION_KEY)
      applySession({ token: '', expiresAt: 0 }, { persist: false })
    }
  } catch (_) {
    window.sessionStorage.removeItem(AUTH_SESSION_KEY)
    applySession({ token: '', expiresAt: 0 }, { persist: false })
  }
}

function handleStorage(event) {
  if (event.key !== AUTH_SESSION_KEY) return
  if (!event.newValue) {
    applySession({ token: '', expiresAt: 0 }, { persist: false })
    now.value = Date.now()
    return
  }
  try {
    const parsed = JSON.parse(event.newValue)
    applySession(
      { token: parsed.token || '', expiresAt: Number(parsed.expiresAt) || 0 },
      { persist: false }
    )
  } catch (_) {
    applySession({ token: '', expiresAt: 0 }, { persist: false })
  }
  now.value = Date.now()
}

function ensureInitialized() {
  if (initialized) return
  initialized = true

  if (typeof window === 'undefined') return

  loadFromStorage()
  window.addEventListener('storage', handleStorage)
  heartbeatId = window.setInterval(() => {
    now.value = Date.now()
    if (session.value.token && !isSessionActive(session.value, now.value)) {
      applySession({ token: '', expiresAt: 0 })
    }
  }, 15000)
}

function setSessionInternal(token, expiresAt = 0) {
  now.value = Date.now()
  applySession({ token, expiresAt })
}

function clearSessionInternal() {
  now.value = Date.now()
  applySession({ token: '', expiresAt: 0 })
}

export function usePostSession() {
  ensureInitialized()

  const isAuthenticated = computed(() => isSessionActive(session.value, now.value))
  const authToken = computed(() => (isAuthenticated.value ? session.value.token : ''))

  return {
    session,
    isAuthenticated,
    authToken,
    setSession: setSessionInternal,
    clearSession: clearSessionInternal,
  }
}

export function installPostSession(app) {
  const { session: authSession, isAuthenticated, authToken, clearSession } = usePostSession()
  app.provide('postAuthSession', authSession)
  app.provide('postIsAuthenticated', isAuthenticated)
  app.provide('postAuthToken', authToken)
  app.provide('postLogout', clearSession)
}

export { isSessionActive }

