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

const expectedUsername = computed(() => import.meta.env.VITE_CHAT_USERNAME?.trim() || '')
const expectedPassword = computed(() => import.meta.env.VITE_CHAT_PASSWORD || '')

const authConfigured = computed(() => Boolean(expectedUsername.value && expectedPassword.value))

async function handleSubmit() {
  errorMessage.value = ''
  if (!authConfigured.value) {
    errorMessage.value = 'Login is not configured. Set VITE_CHAT_USERNAME / VITE_CHAT_PASSWORD.'
    return
  }
  isProcessing.value = true
  try {
    const matches =
      username.value.trim() === expectedUsername.value &&
      password.value === expectedPassword.value
    if (!matches) {
      errorMessage.value = 'Incorrect username or password.'
      password.value = ''
      await nextTick()
      usernameInput.value?.focus()
      return
    }
    emits('authenticated')
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  if (!authConfigured.value) {
    errorMessage.value = 'Login is not configured. Set VITE_CHAT_USERNAME / VITE_CHAT_PASSWORD.'
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
