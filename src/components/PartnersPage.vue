<template>
  <main id="partners">
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div class="intro-copy">
          <h1 class="h2-50">35 partners from academia, industry and the public sector</h1>
          <p class="brodtext-20 muted">
            DTCC is built on collaboration. Our partners represent academia, industry, the public sector, and international networks, creating a broad and balanced foundation for innovation. This diversity ensures that our work is both scientifically rigorous and practically relevant. By combining different forms of expertise, DTCC can address complex urban challenges from multiple angles and turn research into solutions that will help shape tomorrow's cities.
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
            to the Digital Twin Cities Centre.
          </p>
        </header>
        <div class="roster-grid">
          <article v-for="partner in partners" :key="partner.name" class="roster-item card">
            <a
              v-if="partner.url"
              class="partner-link"
              :href="partner.url"
              target="_blank"
              rel="noopener"
            >
              <div class="logo-wrap">
                <img :src="partner.logo" :alt="`${partner.name} logo`">
              </div>
              <div class="name">{{ partner.name }}</div>
            </a>
            <div v-else class="partner-link">
              <div class="logo-wrap">
                <img :src="partner.logo" :alt="`${partner.name} logo`">
              </div>
              <div class="name">{{ partner.name }}</div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="section contact-cta">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Interested in partnering with DTCC?</h2>
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

const graphicSrc = withBase('content/TC-illustration med ringar.webp')
const contactHref = withBase('contact/')

// Load partner logos - using optimized WebP format for better performance
// All 35 partner logos have been converted to WebP (68.6% size reduction: 3.56 MB → 1.12 MB)
const logoModules = import.meta.glob('../../public/content/partners/*.webp', {
  query: '?url',
  import: 'default',
  eager: true,
})

const PARTNER_LINKS = {
  'Ale kommun': 'https://www.ale.se/',
  'Aristotle University': 'https://www.auth.gr/en/',
  Byggstyrning: 'https://www.byggstyrning.se/',
  'Chalmers Industriteknik': 'https://www.chalmersindustriteknik.se/',
  Chalmers: 'https://www.chalmers.se/',
  'Democritus University of Thrace': 'https://www.duth.gr/en',
  'Doing Good': 'https://www.doinggood.se/',
  'Fraunhofer Chalmers': 'https://www.fcc.chalmers.se/',
  'Gdańsk University of Technology': 'https://pg.edu.pl/en',
  'Göteborgs stad': 'https://goteborg.se/',
  'Halmstads kommun': 'https://www.halmstad.se/',
  'Helsingborgs kommun': 'https://helsingborg.se/',
  'Höganäs kommun': 'https://www.hoganas.se/',
  'Högskolan Väst': 'https://www.hv.se/',
  'Kungsbacka kommun': 'https://www.kungsbacka.se/',
  Lantmäteriet: 'https://www.lantmateriet.se/',
  Liljewall: 'https://liljewall.se/',
  'Lindholmen Science Park': 'https://www.lindholmen.se/',
  'Lunds University': 'https://www.lunduniversity.lu.se/',
  'Lunds kommun': 'https://www.lund.se/',
  NCC: 'https://www.ncc.se/',
  NTNU: 'https://www.ntnu.edu/',
  PEAB: 'https://www.peab.se/',
  RISE: 'https://www.ri.se/',
  Ramboll: 'https://ramboll.com/',
  SKR: 'https://skr.se/',
  Skanska: 'https://www.skanska.se/',
  'Sofia University': 'https://www.uni-sofia.bg/eng/',
  Sweco: 'https://www.sweco.se/',
  Twinfinity: 'https://twinfinity.io/',
  'University of Patras': 'https://www.upatras.gr/en/',
  'University of Salento': 'https://international.unisalento.it/',
  'University of Twente': 'https://www.utwente.nl/en/',
  'University of the Aegan': 'https://www.aegean.gr/en/',
  Winniio: 'https://winniio.com/',
}

const partners = computed(() => {
  const entries = Object.entries(logoModules).map(([path, asset]) => {
    const filename = path.split('/').pop() || ''
    const normalized = filename.replace(/\.[^.]+$/, '')
    const displayName = normalized.replace(/[-_]+/g, ' ').replace(/\s+/g, ' ').trim()
    const url = PARTNER_LINKS[displayName] || PARTNER_LINKS[filename] || ''
    return {
      name: displayName,
      logo: asset,
      url,
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
.roster-item {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 220px;
}
.logo-wrap { width: 180px; height: 100px; display: flex; align-items: center; justify-content: center; }
.logo-wrap img { max-width: 100%; max-height: 100%; object-fit: contain; }
.name { font-weight: 600; color: white; font-size: 16px; }
.partner-link {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  text-decoration: none;
  color: inherit;
}
.partner-link:hover .name,
.partner-link:focus-visible .name {
  color: #e35a1d;
}

.contact-cta { padding: 40px 0; background: rgba(0, 0, 0, 0.5); }
.cta-box { padding: 28px; display: flex; flex-direction: column; gap: 16px; align-items: center; text-align: center; }
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: center;
  padding: 12px 32px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: var(--cta-f26a2e);
  border: none;
  border-radius: 8px;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}
.btn-secondary:hover {
  background: #d94e1e;
  transform: translateY(-1px);
}
.btn-secondary:active {
  transform: translateY(0);
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
