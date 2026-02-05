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
      <!-- Hamburger button for mobile -->
      <button
        class="hamburger"
        :class="{ 'open': mobileMenuOpen }"
        @click="toggleMobileMenu"
        aria-label="Toggle navigation menu"
        aria-expanded="mobileMenuOpen"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav class="menu" :class="{ 'mobile-open': mobileMenuOpen }">
        <div class="links">
          <a
            v-for="link in navLinks"
            :key="link.label"
            :href="link.href"
            @click="mobileMenuOpen = false"
          >
            {{ link.label }}
          </a>
        </div>
        <div v-if="isAuthenticated" class="actions">
          <a class="post-link" :href="postHref" @click="mobileMenuOpen = false">Post</a>
          <button
            class="logout-btn"
            type="button"
            @click="handleLogout(); mobileMenuOpen = false"
          >
            Logout
          </button>
        </div>
      </nav>

      <!-- Mobile menu overlay -->
      <div
        v-if="mobileMenuOpen"
        class="mobile-overlay"
        @click="mobileMenuOpen = false"
      ></div>
    </div>
  </header>
</template>

<script setup>
import { computed, inject, ref } from 'vue'

const base = import.meta.env.BASE_URL || '/'
const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const navLinks = [
  { label: 'Projects', href: `${base}projects/` },
  { label: 'Partners', href: `${base}partners/` },
  { label: 'About DTCC', href: `${base}about/` },
  { label: 'News', href: `${base}#news` },
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

/* Hamburger button */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 28px;
  height: 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 100;
}

.hamburger span {
  width: 28px;
  height: 3px;
  background: var(--unnamed-color-fada36);
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.hamburger.open span:nth-child(1) {
  transform: translateY(8px) rotate(45deg);
}

.hamburger.open span:nth-child(2) {
  opacity: 0;
}

.hamburger.open span:nth-child(3) {
  transform: translateY(-8px) rotate(-45deg);
}

/* Mobile overlay */
.mobile-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
  z-index: 90;
}

@media (max-width: 900px) {
  .hamburger {
    display: flex;
  }

  .menu {
    position: fixed;
    top: 72px;
    right: 0;
    width: 280px;
    max-width: 85vw;
    height: calc(100vh - 72px);
    background: linear-gradient(180deg, rgba(8,8,12,0.98) 0%, rgba(10,10,14,0.96) 100%);
    backdrop-filter: saturate(140%) blur(12px);
    border-left: 1px solid rgba(255,255,255,0.08);
    box-shadow: -4px 0 24px rgba(0,0,0,0.4);
    transform: translateX(100%);
    transition: transform 0.3s ease;
    overflow-y: auto;
    z-index: 95;
  }

  .menu.mobile-open {
    transform: translateX(0);
  }

  .mobile-overlay {
    display: block;
  }

  .links {
    display: flex;
    flex-direction: column;
    padding: 24px 20px;
    gap: 0;
  }

  .links a {
    padding: 14px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: 15px;
  }

  .links a:last-child {
    border-bottom: none;
  }

  .actions {
    display: flex;
    flex-direction: column;
    padding: 0 20px 24px;
    gap: 12px;
  }

  .post-link {
    padding: 12px;
    text-align: center;
    border-radius: 6px;
    background: rgba(255,255,255,0.08);
  }

  .logout-btn {
    width: 100%;
  }
}
</style>
