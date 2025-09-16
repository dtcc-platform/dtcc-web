<template>
  <main>
    <!-- Operative management team -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h2-50">Contact page:<br>Operative management team</h1>
          <div class="links">
            <a class="more" :href="base + 'about/'">About us »</a>
          </div>
        </div>
        <div>
          <p class="brodtext-20 muted">
            The operational management team is responsible for the daily operations of the centre,
            including promoting its activities and achievements, managing finances, providing technical support,
            preparing project reports, and maintaining relations with the funding organization.
          </p>
        </div>
      </div>
      <div class="container">
        <div class="people">
          <div class="person" v-for="(p, i) in management" :key="i">
            <div class="avatar" :style="{ backgroundImage: `url(${p.image})` }"></div>
            <div class="name" v-text="p.name" />
            <div class="role muted" v-text="p.role" />
            <a class="more" :href="p.email">Mail to »</a>
          </div>
        </div>
      </div>
    </section>

    <!-- Board of directors -->
    <section class="section gradient-sunrise board">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Board of directors</h2>
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
            <div class="avatar" :style="{ backgroundImage: `url(${p.image})` }"></div>
            <div class="name" v-text="p.name" />
            <div class="role muted" v-text="p.role" />
            <a class="more" :href="p.email">Mail to »</a>
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

const management = [
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img1 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img2 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img1 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img3 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img2 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img3 },
]

const board = [
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img1 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img2 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img3 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img1 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img2 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img3 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img1 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img2 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img3 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img2 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img1 },
  { name: 'Placeholder name', role: 'Placeholder for title', email: '#', image: img3 },
]
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: start; }
.links { margin-top: 8px; }
.more { color: var(--cta-f26a2e); font-weight: 600; }

.people { margin-top: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.person { text-align: left; }
.avatar { height: 160px; border-radius: 12px; background-size: cover; background-position: center; filter: grayscale(20%); }
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

