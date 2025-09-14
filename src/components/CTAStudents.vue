<template>
  <section class="cta">
    <div class="container inner">
      <div class="logo" aria-hidden="true"></div>
      <div class="text">
        <h3 class="h3-30" style="color:#FADA36">We are always looking for talented students to supervise for theses and support the work of the Centre.</h3>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cta { background: #16161b; color: white; padding: 48px 0; }
.inner { display: grid; grid-template-columns: 180px 1fr; gap: 24px; align-items: center; }
.logo { width: 120px; height: 120px; border-radius: 12px; background: linear-gradient(160deg, #9AD7CF, #F6D456); }
@media (max-width: 900px) { .inner { grid-template-columns: 1fr; } .logo { display:none; } }
</style>

