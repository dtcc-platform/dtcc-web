<template>
  <PageShell :showCTA="false">
    <main class="post-main">
      <PostWizard v-if="isAuthenticated" />
      <LoginGate v-else @authenticated="handleAuthenticated" />
    </main>
  </PageShell>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'
import PageShell from './components/PageShell.vue'
import LoginGate from './components/LoginGate.vue'
import LoadingSpinner from './components/LoadingSpinner.vue'
import { usePostSession } from './utils/postSession'

// Lazy load PostWizard (36 KB) - only loads after successful authentication
const PostWizard = defineAsyncComponent({
  loader: () => import('./components/PostWizard.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
  timeout: 10000
})

const { isAuthenticated, setSession } = usePostSession()

function handleAuthenticated(token, expiresAt = 0) {
  setSession(token, expiresAt)
}
</script>

<style scoped>
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
