<template>
  <section id="news" class="section">
    <div class="container grid">
      <div class="media card">
        <div class="media-img" role="img" aria-label="People walking across tram tracks"></div>
        <button class="play" aria-label="Play video">▶</button>
      </div>
      <article class="card note green">
        <span class="eyebrow">News</span>
        <h3 class="h3-30">Placeholder news. Create tool webinar - Join us on June 12th.</h3>
        <p class="brodtext-20 muted">A short intro: years of collaboration, research, and co-creation with cities across Europe, we're excited to ...</p>
        <a href="#" class="more">Read more »</a>
      </article>
      <article class="card note yellow">
        <span class="eyebrow">News</span>
        <h3 class="h3-30">Placeholder news. DTCC kicks off 5-year extension in 2025.</h3>
        <p class="brodtext-20 muted">The Digital Twin Cities Centre (DTCC) is set to embark on its next phase, with a five-year extension approved by ...</p>
        <a href="#" class="more">Read more »</a>
      </article>
    </div>
  </section>
</template>

<style scoped>
.grid { display: grid; grid-template-columns: 1.2fr .8fr .8fr; gap: 20px; align-items: start; }
.media { position: relative; border-radius: 16px; overflow: hidden; }
.media-img { height: 280px; background: url('https://images.unsplash.com/photo-1511497584788-876760111969?q=80&w=1200&auto=format&fit=crop') center/cover no-repeat; filter: saturate(110%); }
.play { position: absolute; inset: auto auto 16px 16px; border: none; border-radius: 50%; width: 48px; height: 48px; background: rgba(255,255,255,0.9); font-size: 18px; cursor: pointer; }
.note { padding: 18px 18px 16px; border-radius: 14px; }
.note.green { background: #D6F1EB; }
.note.yellow { background: #FFE487; }
.more { color: var(--cta-f26a2e); font-weight: 600; }
@media (max-width: 1100px) {
  .grid { grid-template-columns: 1fr; }
  .media-img { height: 220px; }
}
</style>

