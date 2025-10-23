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
            <div :class="['avatar', { placeholder: !(p.image || p.imageFallback) }]">
              <picture v-if="p.image || p.imageFallback">
                <source v-if="p.image" :srcset="p.image" type="image/webp">
                <img
                  :src="p.imageFallback || p.image"
                  :alt="p.name"
                  loading="lazy"
                  decoding="async"
                  :style="{ objectPosition: p.imagePosition || 'center top' }"
                >
              </picture>
            </div>
            <div class="name" v-text="p.name" />
            <div class="role muted" v-text="p.role" />
            <a v-if="p.email" class="more" :href="p.email">Email »</a>
          </div>
        </div>
      </div>
  </section>

    <!-- Technical Board -->
    <section class="section gradient-sunrise technical">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Technical Board</h2>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The Technical Board governs the centre’s research agenda and oversees collaboration between partners.
          </p>
        </div>
      </div>
      <div class="container">
        <div class="people">
          <div class="person" v-for="(p, i) in technicalBoard" :key="i">
            <div :class="['avatar', { placeholder: !(p.image || p.imageFallback) }]">
              <picture v-if="p.image || p.imageFallback">
                <source v-if="p.image" :srcset="p.image" type="image/webp">
                <img
                  :src="p.imageFallback || p.image"
                  :alt="p.name"
                  loading="lazy"
                  decoding="async"
                  :style="{ objectPosition: p.imagePosition || 'center top' }"
                >
              </picture>
            </div>
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
            <div :class="['avatar', { placeholder: !(p.image || p.imageFallback) }]">
              <picture v-if="p.image || p.imageFallback">
                <source v-if="p.image" :srcset="p.image" type="image/webp">
                <img
                  :src="p.imageFallback || p.image"
                  :alt="p.name"
                  loading="lazy"
                  decoding="async"
                  :style="{ objectPosition: p.imagePosition || 'center top' }"
                >
              </picture>
            </div>
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
            <div :class="['avatar', { placeholder: !(p.image || p.imageFallback) }]">
              <picture v-if="p.image || p.imageFallback">
                <source v-if="p.image" :srcset="p.image" type="image/webp">
                <img
                  :src="p.imageFallback || p.image"
                  :alt="p.name"
                  loading="lazy"
                  decoding="async"
                  :style="{ objectPosition: p.imagePosition || 'center top' }"
                >
              </picture>
            </div>
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
  {
    name: 'Anders Logg',
    role: 'Director',
    email: 'mailto:logg@chalmers.se',
    image: contentImage('Anders-Logg-BW.webp'),
    imageFallback: contentImage('Anders-Logg-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Minna Karstunen',
    role: 'Co-Director',
    email: 'mailto:minna.karstunen@chalmers.se',
    image: contentImage('Minna-Karstunen-BW.webp'),
    imageFallback: contentImage('Minna-Karstunen-BW.jpg'),
    imagePosition: 'center 25%',
  },
  {
    name: 'Bernd Ketzler',
    role: 'Scientific Coordinator',
    email: 'mailto:ketzler@chalmers.se',
    image: contentImage('Bernd-Ketzler-BW.webp'),
    imageFallback: contentImage('Bernd-Ketzler-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Vasilis Naserentin',
    role: 'Head of Development',
    email: 'mailto:vasilis.naserentin@chalmers.se',
    image: contentImage('Vasilis-Naserentin-BW.webp'),
    imageFallback: contentImage('Vasilis-Naserentin-BW.jpg'),
    imagePosition: 'center 20%',
  },
  {
    name: 'Nadia Tahir',
    role: 'Communications Officer',
    email: 'mailto:nadia.tahir@chalmers.se',
    image: contentImage('Nadia-Tahir-BW.webp'),
    imageFallback: contentImage('Nadia-Tahir-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Erika Andolf',
    role: 'Financial Officer',
    email: 'mailto:erika.andolf@chalmers.se',
    image: contentImage('Erika-Andolf-BW.webp'),
    imageFallback: contentImage('Erika-Andolf-BW.jpg'),
    imagePosition: 'center top',
  },
]

const boardEntries = [
  {
    name: 'Bo Baudin',
    role: 'SKR',
    image: contentImage('Bo-Baudin-BW.webp'),
    imageFallback: contentImage('Bo-Baudin-BW.jpg'),
  },
  {
    name: 'Johanna Fredhsdotter Lager',
    role: 'NCC',
    image: contentImage('Johanna-Fredsdotter-Lager-BW.webp'),
    imageFallback: contentImage('Johanna-Fredsdotter-Lager-BW.jpg'),
  },
  {
    name: 'Tecumseh Hollis',
    role: 'Höganäs Kommun',
    image: contentImage('Tecumseh-Hollis-BW.webp'),
    imageFallback: contentImage('Tecumseh-Hollis-BW.jpg'),
    imagePosition: 'center 75%',
  },
  {
    name: 'Eric Jeansson',
    role: 'Göteborgs Kommun',
    image: contentImage('Eric-Jeansson-BW.webp'),
    imageFallback: contentImage('Eric-Jeansson-BW.jpg'),
    imagePosition: 'center 35%',
  },
  {
    name: 'Mila Koeva',
    role: 'University of Twente',
    image: contentImage('Mila-Koeva-BW.webp'),
    imageFallback: contentImage('Mila-Koeva-BW.jpg'),
    imagePosition: 'center 32%',
  },
  {
    name: 'Oskar Modin',
    role: 'Chalmers',
    image: contentImage('Oskar-Modin-BW.webp'),
    imageFallback: contentImage('Oskar-Modin-BW.jpg'),
  },
  {
    name: 'Peter Samuelsson',
    role: 'Skanska',
    image: contentImage('Peter-Samuelsson-BW.webp'),
    imageFallback: contentImage('Peter-Samuelsson-BW.jpg'),
  },
  {
    name: 'Lina Vicsai',
    role: 'Ramboll',
    image: contentImage('Lina-Viscai-BW.webp'),
    imageFallback: contentImage('Lina-Viscai-BW.jpg'),
  },
  {
    name: 'Cecilia Windh',
    role: 'LILJEWALL',
    image: contentImage('Cecilia-Windh-BW.webp'),
    imageFallback: contentImage('Cecilia-Windh-BW.jpg'),
  },
]

const board = boardEntries

const advisoryEntries = [
  {
    name: 'Alexandra Bolton',
    role: 'National Centre for Earth Observation, UK',
    image: contentImage('Alexandra-Bolton-BW.webp'),
    imageFallback: contentImage('Alexandra-Bolton-BW.jpg'),
  },
  {
    name: 'Thomas Kolbe',
    role: 'Technical University of Munich, DE',
    image: contentImage('Thomas-H-Kolbe-BW.webp'),
    imageFallback: contentImage('Thomas-H-Kolbe-BW.jpg'),
  },
  {
    name: 'Jantien Stoter',
    role: 'Delft University of Technology, NL',
    image: contentImage('Jantien-Stoter-BW.webp'),
    imageFallback: contentImage('Jantien-Stoter-BW.jpg'),
  },
]

const advisory = advisoryEntries

const technicalBoard = [
  {
    name: 'Alexander Hollberg',
    role: 'Chalmers',
    image: contentImage('Alexander-Hollberg-BW.webp'),
    imageFallback: contentImage('Alexander-Hollberg-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Franziska Hunger',
    role: 'Fraunhoffer Chalmers Centre',
    image: contentImage('Franziska-Hunger-BW.webp'),
    imageFallback: contentImage('Franziska-Hunger-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Minna Karstunen',
    role: 'Chalmers',
    image: contentImage('Minna-Karstunen-BW.webp'),
    imageFallback: contentImage('Minna-Karstunen-BW.jpg'),
    imagePosition: 'center 25%',
  },
  {
    name: 'Anders Logg',
    role: 'Chalmers',
    image: contentImage('Anders-Logg-BW.webp'),
    imageFallback: contentImage('Anders-Logg-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Vasilis Naserentin',
    role: 'Chalmers',
    image: contentImage('Vasilis-Naserentin-BW.webp'),
    imageFallback: contentImage('Vasilis-Naserentin-BW.jpg'),
    imagePosition: 'center 20%',
  },
  {
    name: 'Leonardo Rosado',
    role: 'Chalmers',
    image: contentImage('Leonardo-Rosado-BW.webp'),
    imageFallback: contentImage('Leonardo-Rosado-BW.jpg'),
  },
  {
    name: 'Mattias Roupé',
    role: 'Chalmers',
    image: contentImage('Mattias-Roupe-BW.webp'),
    imageFallback: contentImage('Mattias-Roupe-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Liane Thuvander',
    role: 'Chalmers',
    image: contentImage('Liane-Thuvander-BW.webp'),
    imageFallback: contentImage('Liane-Thuvander-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Tara Wood',
    role: 'Ramboll',
    image: contentImage('Tara-Wood-BW.webp'),
    imageFallback: contentImage('Tara-Wood-BW.jpg'),
  },
  {
    name: 'Dag Wästberg',
    role: 'Chalmers Industriteknik',
    image: contentImage('Dag-Wastberg-BW.webp'),
    imageFallback: contentImage('Dag-Wastberg-BW.jpg'),
    imagePosition: 'center top',
  },
  {
    name: 'Malgorzata Zboinska',
    role: 'Chalmers',
    image: contentImage('Malgorzata-Zboinska-BW.webp'),
    imageFallback: contentImage('Malgorzata-Zboinska-BW.jpg'),
    imagePosition: 'center 38%',
  },
]
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: start; }
.links { margin-top: 8px; }
.more { color: var(--cta-f26a2e); font-weight: 600; }

.people { margin-top: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.person { text-align: left; }
.avatar {
  height: 340px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.06);
}

.avatar picture,
.avatar img {
  display: block;
  width: 100%;
  height: 100%;
}

.avatar img {
  object-fit: cover;
  object-position: center top;
  filter: grayscale(20%);
}

.avatar.placeholder {
  background: rgba(255, 255, 255, 0.03);
}
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
