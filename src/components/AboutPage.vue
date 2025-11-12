<template>
  <main>
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h2-50">About DTCC:<br>Our vision and our mission</h1>
          <a class="more" href="#contact">Contact us »</a>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The Digital Twin Cities Centre (DTCC) is a national research centre based at Chalmers University of Technology. Together with municipalities, industry leaders and international universities, we have been exploring how digital twins can make city planning and construction smarter, more sustainable, and more people-focused since 2020.
          </p>
          <p class="brodtext-20 muted">
            Our projects bring together PhD students, researchers, and practitioners who co-create practical tools for urban planning, construction, and sustainability. DTCC acts as a collaborative arena, where research meets real-world challenges to help cities become more liveable, efficient, and resilient.
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
            The vision of DTCC is to establish Sweden as a world leader in digital twin cities by 2030. We aim to make digital twins the main tool for developing sustainable, intelligent, and liveable cities and regions. By combining openness, collaboration, and cutting-edge research, we want to transform how society plans, builds, and manages the urban environment.
          </p>
          <p class="brodtext-20 muted">
            Digital twins will not only help cities become smarter and more efficient, but also healthier, more resilient, and more inclusive. The ultimate goal is to create urban environments that improve the well-being of citizens, reduce environmental impact, and contribute to the UN Sustainable Development Goals.
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
            Our mission is to unite researchers, municipalities, and industry in developing and applying digital twin technology for real societal benefit. We promote open, interoperable, and federated digital twins — an ecosystem of connected systems rather than monolithic solutions. By advancing common frameworks and principles, we enable data sharing across organisations and sectors, fostering outcome-driven approaches. Through open and interoperable platforms, we turn complex urban data into accessible insights that support better planning, design, and construction. Combining cutting-edge research with practical applications, we train the next generation of experts and help cities and businesses tackle urgent challenges. Through strong international collaborations, we strengthen Sweden's role in the global digital twin movement and ensure our solutions create impact both locally and worldwide.
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

