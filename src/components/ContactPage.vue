<template>
  <main>
    <!-- Operative management team -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h3-30">Operative management team</h1>
          <div class="links">
            <a class="more" :href="base + 'about/'">About us »</a>
          </div>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The Operational Management Team is responsible for the daily operations of the centre,
            including promoting its activities and achievements, managing finances, providing technical support,
            preparing project reports, and maintaining relations with the funding organization.
          </p>
        </div>
      </div>
      <div class="container">
        <div class="people">
          <div class="person" v-for="(p, i) in management" :key="i">
            <div class="avatar" :style="p.image ? { backgroundImage: `url(${p.image})` } : undefined"></div>
            <div class="name" v-text="p.name" />
            <div class="role muted" v-text="p.role" />
          </div>
        </div>
      </div>
    </section>

    <!-- Board of directors -->
    <section class="section gradient-sunrise board">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Board of Directors</h2>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The Centre Board is the highest decision‑making authority, responsible for defining the DTCC strategy,
            monitoring objectives and ensuring their alignment with the overall strategy, overseeing results exploitation
            strategies, approving milestones, and safeguarding intellectual property rights (IPR).
          </p>
        </div>
      </div>
      <div class="container">
        <div class="people">
          <div class="person" v-for="(p, i) in board" :key="i">
            <div class="avatar" :style="p.image ? { backgroundImage: `url(${p.image})` } : undefined"></div>
            <div class="name" v-text="p.name" />
            <div class="role muted" v-text="p.role" />
          </div>
        </div>
      </div>
    </section>

    <!-- International Advisory Board -->
    <section class="section gradient-sunrise advisory">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">International Advisory Board</h2>
        </div>
        <div>
          <p class="brodtext-20 muted">
            External advisors provide independent perspectives, benchmark DTCC internationally, and suggest
            new collaborations that strengthen our research agenda.
          </p>
        </div>
      </div>
      <div class="container">
        <div class="people">
          <div class="person" v-for="(p, i) in advisory" :key="i">
            <div class="avatar" :style="p.image ? { backgroundImage: `url(${p.image})` } : undefined"></div>
            <div class="name" v-text="p.name" />
            <div class="role muted" v-text="p.role" />
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
const base = import.meta.env.BASE_URL || '/'

const img1 = 'https://images.unsplash.com/photo-1544723795-3fb6469f5b39?q=80&w=800&auto=format&fit=crop'
const img2 = 'https://images.unsplash.com/photo-1531123414780-f74287bb2a3b?q=80&w=800&auto=format&fit=crop'
const img3 = 'https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=800&auto=format&fit=crop'

const contentImage = (filename) => `${base}content/${filename}`

const management = [
  { name: 'Anders Logg', role: 'Director', email: 'mailto:logg@chalmers.se', image: contentImage('Anders-Logg-BW.jpg') },
  { name: 'Minna Karstunen', role: 'Co-Director', email: 'mailto:minna.karstunen@chalmers.se', image: contentImage('Minna-Karstunen-BW.jpg') },
  { name: 'Bernd Ketzler', role: 'Scientific Coordinator', email: 'mailto:ketzler@chalmers.se', image: contentImage('Bernd-Ketzler-BW.jpg') },
  { name: 'Vasilis Naserentin', role: 'Head of Development', email: 'mailto:vasilis.naserentin@chalmers.se', image: contentImage('Vasilis-Naserentin-BW.jpg') },
  { name: 'Nadia Tahir', role: 'Communications Officer', email: 'mailto:nadia.tahir@chalmers.se', image: contentImage('Nadia-Tahir-BW.jpg') },
  { name: 'Erika Andolf', role: 'Financial Officer', email: 'mailto:erika.andolf@chalmers.se', image: contentImage('Erika-Andolf-BW.jpg') },
]

const boardEntries = [
  { name: 'Bo Baudin', role: 'SKR' },
  { name: 'Johanna Fredhsdotter Lager', role: 'NCC' },
  { name: 'Tecumseh Hollis', role: 'Höganäs Kommun' },
  { name: 'Eric Jeansson', role: 'Göteborgs Kommun' },
  { name: 'Mila Koeva', role: 'University of Twente' },
  { name: 'Oskar Modin', role: 'Chalmers' },
  { name: 'Peter Samuelsson', role: 'Skanska' },
  { name: 'Lina Vicsai', role: 'Ramboll' },
  { name: 'Cecilia Windh', role: 'LILJEWALL' },
]

const board = boardEntries.map((entry) => ({
  ...entry,
  image: '',
}))

const advisoryEntries = [
  { name: 'Alexandra Bolton', role: 'National Centre for Earth Observation, UK' },
  { name: 'Thomas Kolbe', role: 'Technical University of Munich, DE' },
  { name: 'Jantien Stoter', role: 'Delft University of Technology, NL' },
]

const advisoryImages = [img3, img2, img1]
const advisory = advisoryEntries.map((entry, index) => ({
  ...entry,
  image: advisoryImages[index % advisoryImages.length],
}))
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: start; }
.links { margin-top: 8px; }
.more { color: var(--cta-f26a2e); font-weight: 600; }

.people { margin-top: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.person { text-align: left; }
.avatar { height: 300px; border-radius: 12px; background-size: cover; background-position: center; filter: grayscale(20%); }
.name { margin-top: 6px; font-weight: 600; }
.role { font-size: 14px; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .people { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px) {
  .people { grid-template-columns: 1fr; }
}
</style>
