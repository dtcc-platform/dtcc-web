<template>
  <main id="partners">
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div class="intro-copy">
          <p class="eyebrow">Collaborative network</p>
          <h1 class="h2-50">Partners powering the Digital Twin Platform</h1>
          <p class="brodtext-20 muted">
            DTCC brings academia, the public sector, and private industry together to co-develop a national
            Digital Twin platform. The illustration highlights how our shared ecosystem is designed to
            accelerate research, ensure public value, and translate breakthrough solutions into practice.
          </p>
          <p class="brodtext-20 muted">
            Below you can explore the partner landscape and the roles each group plays in pushing the boundaries
            of digital twin technology.
          </p>
        </div>
        <div class="graphic-card card">
          <img :src="graphicSrc" alt="Venn diagram showing collaboration between academia, public sector and private sector within the Digital Twin Platform">
        </div>
      </div>
    </section>

    <section class="section gradient-sunrise pillars">
      <div class="container pillars-grid">
        <article v-for="pillar in pillars" :key="pillar.title" class="pillar card">
          <h2 class="h3-30">{{ pillar.title }}</h2>
          <p class="brodtext-20 muted">{{ pillar.description }}</p>
          <ul v-if="pillar.examples?.length" class="partners-list">
            <li v-for="example in pillar.examples" :key="example">{{ example }}</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="section gradient-sunrise roster">
      <div class="container">
        <header class="roster-header">
          <h2 class="h3-30">Partner organisations</h2>
          <p class="brodtext-20 muted">
            An alphabetical overview of the universities, municipalities, agencies and companies that contribute
            to the Digital Twin Cities Centre. The list updates automatically from <code>public/content/partners</code>.
          </p>
        </header>
        <div class="roster-grid">
          <article v-for="partner in partners" :key="partner.name" class="roster-item card">
            <div class="logo-wrap">
              <img :src="partner.logo" :alt="`${partner.name} logo`">
            </div>
            <div class="name">{{ partner.name }}</div>
          </article>
        </div>
      </div>
    </section>

    <section class="section contact-cta">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Interested in partnering with DTCC?</h2>
          <p class="brodtext-20 muted">
            We welcome organisations that want to experiment, pilot and scale digital twin solutions for
            the built environment. Whether you are exploring research collaboration, innovation projects or
            long-term memberships, we would love to start a conversation.
          </p>
        </div>
        <div class="cta-box card">
          <p class="brodtext-20 muted">
            Get in touch with our management team to discuss partnership opportunities and ongoing initiatives.
          </p>
          <a class="btn-secondary" :href="contactHref">Contact the management team</a>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { withBase } from '../utils/paths.js'

const graphicSrc = withBase('content/TC-illustration med ringar.png')
const contactHref = withBase('contact/')

const logoModules = import.meta.glob('../../public/content/partners/*.{png,jpg,jpeg,svg}', {
  as: 'url',
  eager: true,
})

const partners = computed(() => {
  const entries = Object.entries(logoModules).map(([path, asset]) => {
    const filename = path.split('/').pop() || ''
    const normalized = filename.replace(/\.[^.]+$/, '')
    const displayName = normalized.replace(/[-_]+/g, ' ').replace(/\s+/g, ' ').trim()
    return {
      name: displayName,
      logo: asset,
    }
  })
  entries.sort((a, b) => a.name.localeCompare(b.name, 'sv'))
  return entries
})

const pillars = computed(() => [
  {
    title: 'Private sector',
    description:
      'Industry partners validate new tools, contribute domain knowledge and bring solutions to market through pilot projects and commercial deployments.',
    examples: ['Ramboll', 'Skanska', 'NCC', 'Liljewall'],
  },
  {
    title: 'Public sector',
    description:
      'Municipalities and agencies ensure that platform development aligns with societal challenges, open data policies and long-term planning needs.',
    examples: ['Göteborgs Stad', 'Höganäs Kommun', 'Chalmers Industriteknik'],
  },
  {
    title: 'Academia',
    description:
      'Leading universities advance the science behind digital twins, providing research excellence, doctoral projects and continuous knowledge exchange.',
    examples: ['Chalmers University of Technology', 'Technical University of Munich', 'University of Twente'],
  },
])
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; align-items: center; }
.intro-copy { display: flex; flex-direction: column; gap: 18px; }
.graphic-card { padding: 20px; display: flex; align-items: center; justify-content: center; }
.graphic-card img { width: 100%; height: auto; max-width: 720px; }
.eyebrow { font-size: 14px; letter-spacing: .12em; text-transform: uppercase; color: var(--unnamed-color-fada36); font-weight: 600; }

.pillars { padding-top: 20px; padding-bottom: 40px; }
.pillars-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.pillar { padding: 28px; display: flex; flex-direction: column; gap: 16px; }
.pillar h2 { color: white; }
.partners-list { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 8px; }
.partners-list li { font-weight: 600; color: white; }

.roster { padding: 36px 0; }
.roster-header { max-width: 720px; margin: 0 auto 32px; text-align: center; display: flex; flex-direction: column; gap: 12px; }
.roster-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; }
.roster-item { padding: 20px; display: flex; flex-direction: column; gap: 12px; align-items: center; text-align: center; min-height: 200px; }
.logo-wrap { width: 140px; height: 80px; display: flex; align-items: center; justify-content: center; }
.logo-wrap img { max-width: 100%; max-height: 100%; object-fit: contain; }
.name { font-weight: 600; color: white; font-size: 16px; }

.contact-cta { padding: 40px 0; background: rgba(0, 0, 0, 0.5); }
.cta-box { padding: 28px; display: flex; flex-direction: column; gap: 16px; }
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.55);
  color: white;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  transition: background 0.2s ease, color 0.2s ease;
}
.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  color: var(--unnamed-color-fada36);
}

@media (max-width: 1200px) {
  .pillars-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 900px) {
  .grid2 { grid-template-columns: 1fr; }
  .graphic-card { order: -1; }
}

@media (max-width: 640px) {
  .pillars-grid { grid-template-columns: 1fr; }
  .pillar { padding: 22px; }
  .cta-box { padding: 22px; }
  .roster-item { min-height: 180px; }
}
</style>
