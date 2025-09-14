<template>
  <header class="nav-wrap">
    <div class="container nav-inner">
      <div class="brand">
        <img class="logo" src="/dtcc-logo.png" alt="Digital Twin Cities Centre logo" />
        <div class="brand-text">
          <strong>Digital Twin</strong>
          <strong>Cities Centre</strong>
        </div>
      </div>
      <nav class="menu">
        <a href="#projects">Projects</a>
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
  /* Slightly more transparent (~10% lower opacity) */
  background: linear-gradient(180deg, rgba(8,8,12,0.86) 0%, rgba(10,10,14,0.83) 100%);
  backdrop-filter: saturate(140%) blur(6px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  box-shadow: 0 2px 12px rgba(0,0,0,0.35);
}
.nav-inner { display: flex; align-items: center; justify-content: space-between; height: 72px; }
.brand { display: flex; align-items: center; gap: 10px; color: white; }
.logo { width: 34px; height: auto; display: block; filter: drop-shadow(0 1px 1px rgba(0,0,0,0.35)); }
.brand-text { display: grid; font-size: 12px; line-height: 1; }
.brand-text strong { color: white; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.brand-text span { color: #cfd3da; letter-spacing: .02em; }
.menu { display: flex; gap: 20px; }
.menu a { color: var(--unnamed-color-fada36); font-size: 14px; text-transform: uppercase; letter-spacing: .08em; }
.menu a:hover { color: white; text-decoration: none; }
@media (max-width: 900px) {
  .menu { display: none; }
}
</style>
