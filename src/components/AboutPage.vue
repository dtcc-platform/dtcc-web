<template>
  <main>
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h2-50">About us:<br>Our vision and our mission</h1>
          <a class="more" href="#contact">Contact us »</a>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The Digital Twin Cities Centre (DTCC) at Chalmers University of Technology develops scientifically grounded digital twins — virtual models of real cities. By combining advanced simulation, real‑time data and 3D modelling, DTCC enables researchers, planners and industry to test ideas, analyze urban systems and make informed decisions. Our mission is to drive innovation, reduce risk and support the creation of sustainable, resilient cities for the future.
          </p>
        </div>
      </div>
      <div class="container">
        <div class="hero-img card"></div>
      </div>
    </section>

    <section class="section gradient-sunrise body">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Our vision</h2>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The centre’s vision is to establish the Digital Twin City concept as the foundation for digital planning, design, construction, and management of sustainable, intelligent, and liveable cities and regions throughout Sweden by 2030.
          </p>
          <p class="brodtext-20 muted">
            This will be achieved by serving as a national and collaborative arena with an open Digital Twin platform that enables the exchange and accessibility of relevant spatial, user and qualitative data as well as the development of cutting‑edge tools and methods that support informed decision‑making based on simulations to forecast the response of design interventions. The centre explores, develops, and disseminates digital strategies, services, and business models that deliver value to Swedish society at large.
          </p>
          <p class="brodtext-20 muted">
            All centre activities are motivated by improving the health and wellbeing of citizens and the circularity of materials, buildings, and infrastructure in cities and regions.
          </p>
        </div>
      </div>
    </section>

    <section class="section gradient-sunrise body">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Our mission</h2>
        </div>
        <div>
          <p class="brodtext-20 muted">
            Make Sweden a leading European country in the implementation and utilisation of digital twin cities. Help to enable all Swedish built environment actors to utilise digital twins as a main tool for sustainable and inclusive planning, execution and management. Become recognised as an international leader and a strong contributor to the global research and dissemination of knowledge and practices for digital twin cities.
          </p>
          <p class="brodtext-20 muted">
            Make strong and lasting contributions to fulfilling the UN SDGs at different levels. Support the full integration of the digital twin concept in all parts of the planning process for the Built Environment.
          </p>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .8fr 1.2fr; gap: 28px; align-items: start; }
.hero-img { height: 380px; border-radius: 14px; margin-top: 16px; background: url('https://images.unsplash.com/photo-1469474968028-56623f02e42e?q=80&w=1400&auto=format&fit=crop') center/cover no-repeat; }
.more { color: var(--cta-f26a2e); font-weight: 600; display: inline-block; margin-top: 8px; }

.body { padding-top: 24px; padding-bottom: 24px; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .hero-img { height: 240px; }
}
</style>

