<template>
  <div class="page-shell">
    <HeaderNav />
    <main class="chat-main">
      <PostWizard />
    </main>
    <FooterSection />
  </div>
</template>

<script setup>
import HeaderNav from './components/HeaderNav.vue'
import FooterSection from './components/FooterSection.vue'
import PostWizard from './components/PostWizard.vue'
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
