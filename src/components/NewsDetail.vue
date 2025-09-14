<template>
  <main>
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <div class="eyebrow">News:</div>
          <h1 class="h2-50">Digital Twins for circularity</h1>
        </div>
        <div>
          <p class="brodtext-20 muted">
            After three years of collaboration, research, and co‑creation with cities across Europe, we’re excited to announce that the CREATE tool is finally complete! As part of the EU‑funded DUT project CREATE, we’ve developed an innovative solution to support cities in adopting more circular urban planning practices.
          </p>
          <p class="brodtext-20 muted">
            We’ll be presenting the final version of the tool in a live webinar on June 12th, from 11:30 to 12:30 CET, and we’d love for you to join us.
          </p>
        </div>
      </div>
      <div class="container">
        <div class="hero-img card"></div>
      </div>
    </section>

    <!-- Body gradient section -->
    <section class="section gradient-sunrise body">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Placeholder<br>headline</h2>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The centre’s vision is to establish the Digital Twin City concept as the foundation for digital planning, design, construction, and management of sustainable, intelligent, and liveable cities and regions throughout Sweden by 2030.
          </p>
          <p class="brodtext-20 muted">
            This will be achieved by serving as a national and collaborative arena with an open Digital Twin platform that enables the exchange and accessibility of relevant spatial, user and qualitative data as well as the development of cutting‑edge tools and methods that support informed decision‑making based on simulations to forecast the response of design interventions. The centre explores, develops, and disseminates digital strategies, services, and business models that deliver value to Swedish society at large.
          </p>
        </div>
      </div>
    </section>

    <!-- Contacts -->
    <section class="section contacts">
      <div class="container">
        <h3 class="h3-30">For more information<br>please contact:</h3>
        <div class="people">
          <div class="person">
            <div class="avatar" style="background-image:url('https://images.unsplash.com/photo-1544723795-3fb6469f5b39?q=80&w=800&auto=format&fit=crop')"></div>
            <div class="name">Placeholder name</div>
            <div class="role muted">Placeholder for title</div>
            <a href="#" class="more">Mail to »</a>
          </div>
          <div class="person">
            <div class="avatar" style="background-image:url('https://images.unsplash.com/photo-1531123414780-f74287bb2a3b?q=80&w=800&auto=format&fit=crop')"></div>
            <div class="name">Placeholder name</div>
            <div class="role muted">Placeholder for title</div>
            <a href="#" class="more">Mail to »</a>
          </div>
          <div class="person">
            <div class="avatar" style="background-image:url('https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=800&auto=format&fit=crop')"></div>
            <div class="name">Placeholder name</div>
            <div class="role muted">Placeholder for title</div>
            <a href="#" class="more">Mail to »</a>
          </div>
        </div>
      </div>
    </section>

    <!-- Related posts -->
    <section class="section gradient-sunrise related">
      <div class="container">
        <h3 class="h3-30 section-title">Related posts</h3>
        <div class="cards">
          <article class="card project">
            <div class="img" style="background-image:url('https://images.unsplash.com/photo-1494516192674-b82b5f1e61dc?q=80&w=1200&auto=format&fit=crop')"></div>
            <div class="body">
              <h4 class="h3-30">Placeholder news.</h4>
              <p class="brodtext-20 muted">Urban densification influences wind, temperature, noise, daylight and air quality...</p>
              <a href="#" class="more">Read more »</a>
            </div>
          </article>
          <article class="card project">
            <div class="img" style="background-image:url('https://images.unsplash.com/photo-1518306727298-4c17e1bf6942?q=80&w=1200&auto=format&fit=crop')"></div>
            <div class="body">
              <h4 class="h3-30">Placeholder news.</h4>
              <p class="brodtext-20 muted">Developing decision support systems to help making informed decisions ...</p>
              <a href="#" class="more">Read more »</a>
            </div>
          </article>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: center; }
.hero-img { height: 380px; border-radius: 14px; margin-top: 16px; background: url('https://images.unsplash.com/photo-1526256262350-7da7584cf5eb?q=80&w=1400&auto=format&fit=crop') center/cover no-repeat; }

.body { padding-top: 24px; padding-bottom: 24px; }

.contacts .people { margin-top: 16px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.person { text-align: left; }
.avatar { height: 160px; border-radius: 12px; background-size: cover; background-position: center; filter: grayscale(20%); }
.name { margin-top: 6px; font-weight: 600; }
.role { font-size: 14px; }

.related .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img { height: 180px; background: #ddd center/cover no-repeat; }
.project .body { padding: 14px 16px 18px; }
.project a.more { color: var(--cta-f26a2e); font-weight: 600; }
.section-title { text-align: center; margin-bottom: 20px; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .contacts .people { grid-template-columns: 1fr; }
  .hero-img { height: 240px; }
  .related .cards { grid-template-columns: 1fr; }
}
</style>

