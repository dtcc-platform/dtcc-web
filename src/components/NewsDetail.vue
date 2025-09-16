<template>
  <main v-if="item">
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <div class="eyebrow">News:</div>
          <h1 class="h2-50" v-text="item.title"></h1>
        </div>
        <div>
          <p class="brodtext-20 muted" v-text="item.intro || item.summary || ''" />
        </div>
      </div>
      <div class="container">
        <div class="hero-img card" :style="{ backgroundImage: heroImageStyle }"></div>
      </div>
    </section>

    <!-- Body gradient section -->
    <section class="section gradient-sunrise body">
      <div class="container grid2">
        <div>
          <h2 class="h3-30" v-text="item.subheading || 'Details'" />
        </div>
        <div>
          <p class="brodtext-20 muted" v-for="(p, i) in bodyParas" :key="i" v-text="p" />
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
          <article v-for="r in related" :key="r.id" class="card project">
            <div class="img" :style="{ backgroundImage: r.image ? `url(${r.image})` : undefined }"></div>
            <div class="body">
              <h4 class="h3-30" v-text="r.title" />
              <p class="brodtext-20 muted" v-text="r.summary || ''" />
              <a :href="detailHref(r.id)" class="more">Read more »</a>
            </div>
          </article>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { sanitizeSrc } from '../utils/sanitize'

const params = new URLSearchParams(location.search)
const slug = params.get('slug')
const item = ref(null)
const related = ref([])
const heroImageStyle = computed(() => item.value?.image ? `url(${item.value.image})` : undefined)

const bodyParas = computed(() => {
  const body = item.value?.body || ''
  if (!body) return []
  if (Array.isArray(body)) return body
  return String(body).split(/\n\n+/).map(s => s.trim()).filter(Boolean)
})

const base = import.meta.env.BASE_URL || '/'
const detailHref = (slug) => `${base}news/detail.html?slug=${encodeURIComponent(slug)}`

onMounted(async () => {
  if (!slug) return
  try {
    const r = await fetch(`/content/news/${slug}.json`, { cache: 'no-store' })
    if (!r.ok) return
    const data = await r.json()
    let image = sanitizeSrc(data.image || null)
    if (!image) {
      for (const u of [`/content/news/${slug}.jpeg`, `/content/news/${slug}.jpg`, `/content/news/${slug}.png`]) {
        try { const h = await fetch(u, { method: 'HEAD' }); if (h.ok) { image = sanitizeSrc(u); break } } catch(_) {}
      }
    }
    item.value = {
      id: slug,
      title: data.title || slug,
      intro: data.intro || data.summary || '',
      subheading: data.subheading || data.headline || 'Details',
      body: data.body || '',
      image,
    }
    // Load related posts (up to 2)
    const idx = await fetch('/content/news/index.json', { cache: 'no-store' })
    if (idx.ok) {
      const payload = await idx.json()
      const arr = Array.isArray(payload.items) ? payload.items : Array.isArray(payload) ? payload : []
      const bases = arr.map((it) => (typeof it === 'string' ? { base: it } : it)).filter(it => (it.base || it.name || it.id) !== slug)
      const resolved = []
      for (const it of bases) {
        const base = it.base || it.name || it.id
        let data2 = {}
        try { const r2 = await fetch(`/content/news/${base}.json`, { cache: 'no-store' }); if (r2.ok) data2 = await r2.json() } catch(_) {}
        let img = sanitizeSrc(it.image || data2.image || null)
        if (!img) {
          for (const u of [`/content/news/${base}.jpeg`, `/content/news/${base}.jpg`, `/content/news/${base}.png`]) {
            try { const h = await fetch(u, { method: 'HEAD' }); if (h.ok) { img = sanitizeSrc(u); break } } catch(_) {}
          }
        }
        if (!img) continue
        resolved.push({ id: base, title: data2.title || base, summary: data2.summary || data2.excerpt || '', image: img, date: data2.date || null, order: Number(data2.order) })
      }
      if (resolved.some(x => Number.isFinite(x.order))) {
        resolved.sort((a, b) => (a.order ?? 1e9) - (b.order ?? 1e9))
      } else {
        resolved.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
      }
      related.value = resolved.slice(0, 2)
    }
  } catch (_) {}
})
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: center; }
.hero-img { height: 380px; border-radius: 14px; margin-top: 16px; background: #000 center/cover no-repeat; }

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
