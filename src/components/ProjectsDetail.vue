<template>
  <main v-if="item">
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <div class="eyebrow">Project:</div>
          <h1 class="h2-50" v-text="item.title"></h1>
        </div>
        <div>
          <p class="brodtext-20 muted" v-text="item.intro || item.summary || ''" />
          <div v-if="item.url" class="visit">
            <a class="more" :href="item.url" target="_blank" rel="noopener">Visit website »</a>
          </div>
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

    <!-- Related projects -->
    <section class="section gradient-sunrise related">
      <div class="container">
        <h3 class="h3-30 section-title">Related projects</h3>
        <div class="cards">
          <article v-for="r in related" :key="r.id" class="card project">
            <div class="img" :style="{ backgroundImage: r.image ? `url(${r.image})` : undefined }"></div>
            <div class="body">
              <h4 class="h3-30" v-text="r.title" />
              <p class="brodtext-20 muted" v-text="r.summary || r.description || ''" />
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
import { sanitizeSrc, sanitizeUrl } from '../utils/sanitize'
import { withBase, resolveUrl } from '../utils/paths.js'

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

const detailHref = (slug) => withBase(`projects/detail.html?slug=${encodeURIComponent(slug)}`)

const normalizeImage = (value) => {
  if (!value) return null
  return sanitizeSrc(resolveUrl(value))
}

const normalizeLink = (value) => {
  if (!value) return ''
  const trimmed = value.trim()
  if (!trimmed || trimmed === '#') return ''
  const resolved = resolveUrl(trimmed)
  if (typeof resolved !== 'string') return ''
  return resolved.startsWith('/') ? resolved : sanitizeUrl(resolved)
}

onMounted(async () => {
  if (!slug) return
  try {
    const r = await fetch(resolveUrl(`content/projects/${slug}.json`), { cache: 'no-store' })
    if (!r.ok) return
    const data = await r.json()
    let image = normalizeImage(data.image || null)
    if (!image) {
      for (const u of ['jpeg', 'jpg', 'png'].map(ext => resolveUrl(`content/projects/${slug}.${ext}`))) {
        try { const h = await fetch(u, { method: 'HEAD' }); if (h.ok) { image = sanitizeSrc(u); break } } catch(_) {}
      }
    }
    item.value = {
      id: slug,
      title: data.title || data.name || slug,
      intro: data.intro || data.summary || data.description || '',
      subheading: data.subheading || data.headline || 'Details',
      body: data.body || data.details || '',
      image,
      url: normalizeLink(data.url || data.link || ''),
      date: data.date || data.updated || null,
    }
    // Load related projects (up to 2)
    const idx = await fetch(withBase('content/projects/index.json'), { cache: 'no-store' })
    if (idx.ok) {
      const payload = await idx.json()
      const arr = Array.isArray(payload.items) ? payload.items : Array.isArray(payload) ? payload : []
      const bases = arr
        .map((it) => (typeof it === 'string' ? { base: it } : it))
        .filter(it => (it.base || it.name || it.id) !== slug)
      const resolved = []
      for (const it of bases) {
        const baseSlug = it.base || it.name || it.id
        let data2 = {}
        try { const r2 = await fetch(resolveUrl(`content/projects/${baseSlug}.json`), { cache: 'no-store' }); if (r2.ok) data2 = await r2.json() } catch(_) {}
        let img = normalizeImage(it.image || data2.image || null)
        if (!img) {
          for (const u of ['jpeg', 'jpg', 'png'].map(ext => resolveUrl(`content/projects/${baseSlug}.${ext}`))) {
            try { const h = await fetch(u, { method: 'HEAD' }); if (h.ok) { img = sanitizeSrc(u); break } } catch(_) {}
          }
        }
        if (!img) continue
        resolved.push({ id: baseSlug, title: data2.title || data2.name || baseSlug, summary: data2.summary || data2.excerpt || data2.description || '', image: img, date: data2.date || null, order: Number(data2.order) })
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
.visit { margin-top: 10px; }

.body { padding-top: 24px; padding-bottom: 24px; }

.related .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img { height: 180px; background: #ddd center/cover no-repeat; }
.project .body { padding: 14px 16px 18px; }
.project a.more { color: var(--cta-f26a2e); font-weight: 600; }
.section-title { text-align: center; margin-bottom: 20px; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .hero-img { height: 240px; }
  .related .cards { grid-template-columns: 1fr; }
}
</style>
