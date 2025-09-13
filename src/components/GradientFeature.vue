<template>
  <section class="feature">
    <div class="gradient-sunrise angled">
      <div class="container inner">
        <div class="left">
          <h2 class="h2-50">Creating<br>liveable<br>cities.</h2>
        </div>
        <div class="right">
          <div class="img" role="img" aria-label="City simulation"></div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.feature { margin: 40px 0; }
.angled { transform: skewY(-3deg); padding: 48px 0; }
.inner { transform: skewY(3deg); display: grid; grid-template-columns: .9fr 1.1fr; gap: 24px; align-items: center; }
.left { padding: 48px 0; }
.right .img { height: 340px; border-radius: 14px; background: url('https://images.unsplash.com/photo-1541336032412-2048a678540d?q=80&w=1400&auto=format&fit=crop') center/cover no-repeat; box-shadow: var(--shadow-card); }
@media (max-width: 900px) { .inner { grid-template-columns: 1fr; } .right .img { height: 220px; } }
</style>

