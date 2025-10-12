<template>
  <div class="login-shell container">
    <section class="login card">
      <header class="login-header">
        <h1>Restricted access</h1>
        <p class="muted">
          Enter the editor credentials to continue. Reach out to the DTCC web team if you need access.
        </p>
      </header>

      <form class="login-form" @submit.prevent="handleSubmit">
        <div class="field">
          <label for="login-username">Username</label>
          <input
            id="login-username"
            ref="usernameInput"
            v-model.trim="username"
            type="text"
            autocomplete="username"
            placeholder="dtcc-editor"
            required
          >
        </div>

        <div class="field">
          <label for="login-password">Password</label>
          <input
            id="login-password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
          >
        </div>

        <button type="submit" class="btn-primary" :disabled="isProcessing">
          <span v-if="isProcessing">Signing in…</span>
          <span v-else>Sign in</span>
        </button>

        <transition name="fade">
          <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        </transition>
      </form>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const emits = defineEmits(['authenticated'])

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isProcessing = ref(false)
const usernameInput = ref(null)

const authEndpoint = computed(() => import.meta.env.VITE_POST_AUTH_URL?.trim() || '')

async function handleSubmit() {
  errorMessage.value = ''
  if (!authEndpoint.value) {
    errorMessage.value = 'Login endpoint is not configured. Set VITE_POST_AUTH_URL.'
    return
  }
  isProcessing.value = true
  try {
    const response = await fetch(authEndpoint.value, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value,
      }),
    })

    const payload = await response.json().catch(() => ({}))

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error(payload?.error || 'Invalid username or password.')
      }
      const message = typeof payload?.error === 'string' && payload.error
        ? payload.error
        : `Login failed (status ${response.status})`
      throw new Error(message)
    }

    if (!payload?.token || typeof payload.token !== 'string') {
      throw new Error('Login response missing token.')
    }

    const expiresAt = Number(payload?.expiresAt) || 0
    emits('authenticated', payload.token, expiresAt)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
    password.value = ''
    await nextTick()
    usernameInput.value?.focus()
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  if (!authEndpoint.value) {
    errorMessage.value = 'Login endpoint is not configured. Set VITE_POST_AUTH_URL.'
  } else {
    nextTick(() => {
      usernameInput.value?.focus()
    })
  }
})
</script>

<style scoped>
.login-shell {
  display: flex;
  justify-content: center;
  width: 100%;
}

.login {
  width: min(520px, 100%);
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 36px 40px;
  align-self: center;
}

.login-header h1 {
  margin-bottom: 12px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field input {
  font: inherit;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid #d0d0d8;
  background: #fff;
  color: inherit;
}

.btn-primary {
  align-self: flex-start;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  background: var(--cta-f26a2e);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: progress;
}

.alert.error {
  margin: 0;
  color: #c0392b;
  font-weight: 600;
}
</style>
