<template>
  <footer class="footer">
    <div class="container grid">
      <div class="brand">
        <img class="logo" src="/dtcc-logo.png" alt="Digital Twin Cities Centre logo" />
        <div class="brand-text">
          <strong>Digital Twin</strong>
          <strong>Cities Centre</strong>
        </div>
      </div>
      <div>
        <div class="eyebrow">Address</div>
        <div class="brodtext-20 muted">Kvarnberg, Lab<br/>Sven Hultins gata 6,<br/>Gothenburg, Sweden</div>
      </div>
      <div>
        <div class="eyebrow">Contact</div>
        <div class="brodtext-20 muted">Bernd Ketzler<br/>Scientific Coordinator<br/>dtcc@chalmers.se</div>
      </div>
      <div>
        <div class="eyebrow">Follow</div>
        <div class="brodtext-20 muted"><a href="#">LinkedIn</a><br/><a href="#">Instagram</a></div>
      </div>
    </div>
    <div class="container legal">
      <div class="brodtext-20 muted">Chalmers University of Technology © 2025</div>
    </div>
  </footer>
</template>

<style scoped>
.footer { background: #0f0f14; color: white; padding: 40px 0 24px; }
.grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 28px; align-items: start; }
.brand { display: flex; align-items: center; gap: 10px; color: white; }
.logo { width: 34px; height: auto; display: block; filter: drop-shadow(0 1px 1px rgba(0,0,0,0.35)); }
.brand-text { display: grid; font-size: 12px; line-height: 1; }
.brand-text strong { color: white; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.eyebrow { color: var(--unnamed-color-fada36); }
.grid .brodtext-20 { color: #ffffff; }
.grid .brodtext-20 a { color: #ffffff; text-decoration: none; }
.grid .brodtext-20 a:hover { text-decoration: underline; }
.legal { border-top: 1px solid rgba(255,255,255,0.08); margin-top: 20px; padding-top: 16px; color: var(--unnamed-color-fada36); text-align: center; }
/* Ensure legal text stays yellow even if it has .muted */
.legal .brodtext-20,
.legal .muted { color: var(--unnamed-color-fada36); }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
</style>
