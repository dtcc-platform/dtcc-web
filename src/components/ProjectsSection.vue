<template>
  <section id="projects" class="section">
    <div class="container">
      <h3 class="h3-30" style="text-align:center;margin-bottom:20px">Latest projects</h3>
      <div class="cards">
        <article class="card project">
          <div class="img" style="background-image:url('https://images.unsplash.com/photo-1494516192674-b82b5f1e61dc?q=80&w=1200&auto=format&fit=crop')"></div>
          <div class="body">
            <h4 class="h3-30">Urban Environmental Comfort Design</h4>
            <p class="brodtext-20 muted">Urban densification influences wind, temperature, noise, daylight and air quality at both city scale and ...</p>
            <a href="#">Read more »</a>
          </div>
        </article>
        <article class="card project">
          <div class="img" style="background-image:url('https://images.unsplash.com/photo-1518306727298-4c17e1bf6942?q=80&w=1200&auto=format&fit=crop')"></div>
          <div class="body">
            <h4 class="h3-30">4D digital twin for underground, and natural hazards</h4>
            <p class="brodtext-20 muted">Developing decision support systems to help making informed decisions ...</p>
            <a href="#">Read more »</a>
          </div>
        </article>
        <article class="card project">
          <div class="img" style="background-image:url('https://images.unsplash.com/photo-1517153295259-74eb0b401b47?q=80&w=1200&auto=format&fit=crop')"></div>
          <div class="body">
            <h4 class="h3-30">Mobility and the liveable city</h4>
            <p class="brodtext-20 muted">A city-scale twin helps us test street redesigns, public realm and network impacts ...</p>
            <a href="#">Read more »</a>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.project .img { height: 180px; background: #ddd center/cover no-repeat; }
.project .body { padding: 14px 16px 18px; }
.project a { color: var(--cta-f26a2e); font-weight: 600; }
@media (max-width: 1100px) { .cards { grid-template-columns: 1fr 1fr; } }
@media (max-width: 700px) { .cards { grid-template-columns: 1fr; } }
</style>

