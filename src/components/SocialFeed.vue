<template>
  <section class="section">
    <div class="container">
      <div class="carousel">
        <div class="card post" v-for="i in 3" :key="i">
          <div class="post-header">
            <div class="avatar"></div>
            <div class="meta">
              <strong>Microsoft</strong>
              <span class="muted"> · {{ i === 1 ? 'Just now' : i === 2 ? '3 hours ago' : '2 days ago' }}</span>
            </div>
            <span class="badge">in</span>
          </div>
          <div class="img"></div>
          <div class="post-body brodtext-20 muted">Explore the unique creations of talented artists, designers and writers that showcase the limitless potential of using AI...</div>
          <div class="post-actions muted">♡ 128 · Share</div>
        </div>
      </div>
      <div class="pager">
        <span class="dot active"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.carousel { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.post { padding: 12px; }
.post-header { display: flex; align-items: center; gap: 10px; }
.avatar { width: 28px; height: 28px; border-radius: 6px; background: #0056b3; }
.badge { margin-left: auto; background: #0a66c2; color: white; font-size: 12px; padding: 2px 6px; border-radius: 4px; }
.img { height: 160px; background: url('https://images.unsplash.com/photo-1526498460520-4c246339dccb?q=80&w=1200&auto=format&fit=crop') center/cover no-repeat; border-radius: 8px; margin: 8px 0; }
.post-actions { font-size: 14px; }
.pager { display: flex; justify-content: center; gap: 8px; margin-top: 12px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #d6d6da; }
.dot.active { background: #6c6c74; }
@media (max-width: 1100px) { .carousel { grid-template-columns: 1fr 1fr; } }
@media (max-width: 700px) { .carousel { grid-template-columns: 1fr; } }
</style>

