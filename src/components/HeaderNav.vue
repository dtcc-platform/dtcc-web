<template>
  <header class="nav-wrap">
    <div class="container nav-inner">
      <a class="brand" :href="base" aria-label="Digital Twin Cities Centre — Home">
        <img class="logo" :src="base + 'dtcc-logo.png'" alt="Digital Twin Cities Centre logo" />
        <div class="brand-text">
          <strong>Digital Twin</strong>
          <strong>Cities Centre</strong>
        </div>
      </a>
      <nav class="menu">
        <div class="links">
          <a v-for="link in navLinks" :key="link.label" :href="link.href">{{ link.label }}</a>
        </div>
        <div v-if="isAuthenticated" class="actions">
          <a class="post-link" :href="postHref">Post</a>
          <button
            class="logout-btn"
            type="button"
            @click="handleLogout"
          >
            Logout
          </button>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { computed, inject } from 'vue'

const base = import.meta.env.BASE_URL || '/'

const navLinks = [
  { label: 'Projects', href: `${base}projects/` },
  { label: 'Partners', href: '#partners' },
  { label: 'About us', href: `${base}about/` },
  { label: 'News', href: `${base}news/` },
  { label: 'Events', href: `${base}events/`, disabled: true },
  { label: 'Gallery', href: `${base}gallery/` },
  { label: 'Contact', href: `${base}contact/` },
].filter((link) => !link.disabled)

const injectedAuth = inject('postIsAuthenticated', null)
const logoutFn = inject('postLogout', null)
const postHref = `${base}post/`

const isAuthenticated = computed(() => {
  if (injectedAuth && typeof injectedAuth === 'object' && 'value' in injectedAuth) {
    return Boolean(injectedAuth.value)
  }
  return Boolean(injectedAuth)
})

function handleLogout() {
  if (typeof logoutFn === 'function') {
    logoutFn()
  }
}
</script>

<style scoped>
.nav-wrap {
  position: sticky;
  top: 0;
  z-index: 10;
  background: linear-gradient(180deg, rgba(8,8,12,0.86) 0%, rgba(10,10,14,0.83) 100%);
  backdrop-filter: saturate(140%) blur(6px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  box-shadow: 0 2px 12px rgba(0,0,0,0.35);
}
.nav-inner { display: flex; align-items: center; justify-content: space-between; height: 72px; }
.brand { display: flex; align-items: center; gap: 10px; color: white; text-decoration: none; }
.logo { width: 34px; height: auto; display: block; filter: drop-shadow(0 1px 1px rgba(0,0,0,0.35)); }
.brand-text { display: grid; font-size: 12px; line-height: 1; text-transform: uppercase; letter-spacing: .06em; }
.brand-text strong { color: white; font-weight: 700; }
.menu { display: flex; gap: 20px; align-items: center; }
.links { display: flex; gap: 20px; align-items: center; }
.actions { display: flex; gap: 16px; align-items: center; }
.menu a { color: var(--unnamed-color-fada36); font-size: 14px; text-transform: uppercase; letter-spacing: .08em; }
.menu a:hover { color: white; text-decoration: none; }
.post-link { color: white; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.post-link:hover { color: var(--unnamed-color-fada36); }
.logout-btn {
  border: 1px solid rgba(255,255,255,0.4);
  background: transparent;
  color: white;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}
.logout-btn:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.6);
}
@media (max-width: 900px) {
  .links { display: none; }
  .menu { gap: 12px; }
}
</style>
