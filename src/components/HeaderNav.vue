<template>
  <header class="nav-wrap">
    <div class="container nav-inner">
      <div class="brand">
        <div class="logo" aria-hidden="true" />
        <div class="brand-text">
          <strong>Digital Twin</strong>
          <span>Cities Centre</span>
        </div>
      </div>
      <nav class="menu">
        <a href="#projects">Products</a>
        <a href="#partners">Partners</a>
        <a href="#about">About us</a>
        <a href="#news">News</a>
        <a href="#events">Events</a>
        <a href="#contact">Contact</a>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.nav-wrap {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(16,16,22,0.7);
  backdrop-filter: saturate(140%) blur(6px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.nav-inner { display: flex; align-items: center; justify-content: space-between; height: 72px; }
.brand { display: flex; align-items: center; gap: 12px; color: white; }
.logo { width: 36px; height: 36px; border-radius: 8px; background: linear-gradient(160deg, #9AD7CF, #F6D456); }
.brand-text { display: grid; font-size: 12px; line-height: 1; }
.brand-text strong { color: white; font-weight: 700; letter-spacing: .02em; }
.brand-text span { color: #cfd3da; letter-spacing: .02em; }
.menu { display: flex; gap: 20px; }
.menu a { color: var(--unnamed-color-fada36); font-size: 14px; text-transform: uppercase; letter-spacing: .08em; }
.menu a:hover { color: white; text-decoration: none; }
@media (max-width: 900px) {
  .menu { display: none; }
}
</style>

