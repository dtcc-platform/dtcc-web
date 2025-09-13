<template>
  <footer class="footer">
    <div class="container grid">
      <div class="brand">
        <div class="logo"></div>
        <div>
          <strong>Digital Twin Cities Centre</strong>
        </div>
      </div>
      <div>
        <div class="eyebrow">Address</div>
        <div class="brodtext-20 muted">Kvarnberg, Lab<br/>Sven Hultins gata 6,<br/>Gothenburg, Sweden</div>
      </div>
      <div>
        <div class="eyebrow">Contact</div>
        <div class="brodtext-20 muted">Martin Nauer<br/>Student & Coordinator<br/>dtcc@chalmers.se</div>
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
.brand { display: flex; align-items: center; gap: 12px; }
.logo { width: 42px; height: 42px; border-radius: 8px; background: linear-gradient(160deg, #9AD7CF, #F6D456); }
.legal { border-top: 1px solid rgba(255,255,255,0.08); margin-top: 20px; padding-top: 16px; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
</style>

