<template>
  <section id="news" class="section">
    <div class="container grid">
      <div class="media card">
        <div class="media-img" role="img" aria-label="People walking across tram tracks"></div>
        <button class="play" aria-label="Play video">▶</button>
      </div>

      <template v-if="items.length">
        <article v-for="(n, idx) in items" :key="n.id" class="card note" :class="idx % 2 ? 'yellow' : 'green'">
          <img v-if="n.image" :src="n.image" :alt="n.title" class="thumb" loading="lazy" decoding="async" />
          <span class="eyebrow">{{ n.eyebrow || 'News' }}</span>
          <h3 class="h3-30" v-text="n.title" />
          <p class="brodtext-20 muted" v-text="n.summary || n.excerpt" />
          <a :href="n.url || n.link || '#'" class="more">Read more »</a>
        </article>
      </template>
      <template v-else>
        <article class="card note green">
          <span class="eyebrow">News</span>
          <h3 class="h3-30">Placeholder news. Create tool webinar - Join us on June 12th.</h3>
          <p class="brodtext-20 muted">A short intro: years of collaboration, research, and co-creation with cities across Europe, we're excited to ...</p>
          <a href="#" class="more">Read more »</a>
        </article>
        <article class="card note yellow">
          <span class="eyebrow">News</span>
          <h3 class="h3-30">Placeholder news. DTCC kicks off 5-year extension in 2025.</h3>
          <p class="brodtext-20 muted">The Digital Twin Cities Centre (DTCC) is set to embark on its next phase, with a five-year extension approved by ...</p>
          <a href="#" class="more">Read more »</a>
        </article>
      </template>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { sanitizeUrl, sanitizeSrc } from '../utils/sanitize'
import { withBase, resolveUrl, getOptimizedImageUrl } from '../utils/paths.js'

// Load JSON files and images from src/news
// Each item requires a matching image with the same base name
const jsonModules = import.meta.glob('../news/*.json', { eager: true, import: 'default' })
const imageModules = import.meta.glob('../news/*.{jpg,jpeg,png,webp}', { eager: true, import: 'default' })

// Runtime-loaded items from /public/news via fetch
const runtimeItems = ref([])

const normalizeImage = (value) => {
  if (!value) return null
  const optimized = getOptimizedImageUrl(value)
  return sanitizeSrc(resolveUrl(optimized))
}

const normalizeLink = (value) => {
  if (!value) return '#'
  const trimmed = value.trim()
  if (!trimmed || trimmed === '#') return '#'
  const resolved = resolveUrl(trimmed)
  if (typeof resolved !== 'string') return '#'
  return resolved.startsWith('/') ? resolved : sanitizeUrl(resolved)
}

onMounted(async () => {
  try {
    const idx = await fetch(withBase('content/news/index.json'), { cache: 'no-store' })
    if (!idx.ok) return
    const payload = await idx.json()
    const arr = Array.isArray(payload.items) ? payload.items : Array.isArray(payload) ? payload : []
    const bases = arr.map((it) => {
      if (typeof it === 'string') return { base: it }
      return it
    })

    const resolved = []
    for (const it of bases) {
      const base = it.base || it.name || it.file || it.id
      const jsonPath = it.json || (base ? `content/news/${base}.json` : null)
      let data = {}
      if (jsonPath) {
        try {
          const r = await fetch(resolveUrl(jsonPath), { cache: 'no-store' })
          if (r.ok) data = await r.json()
        } catch (_) { /* ignore */ }
      }
      const title = it.title || data.title || data.headline || base || 'Untitled'
      const summary = it.summary || data.summary || data.excerpt || ''
      const url = normalizeLink(it.url || data.url || data.link || '')
      const eyebrow = it.eyebrow || data.eyebrow || 'News'
      const date = it.date || data.date || data.published || data.publishedAt || data.time || null

      let image = normalizeImage(it.image || data.image || null)
      if (!image && base) {
        // Probe for available local image extension (prefer WebP)
        const tryUrls = ['webp', 'jpeg', 'jpg', 'png']
          .map(ext => resolveUrl(`content/news/${base}.${ext}`))
        for (const u of tryUrls) {
          try {
            const head = await fetch(u, { method: 'HEAD' })
            if (head.ok) { image = sanitizeSrc(u); break }
          } catch (_) { /* ignore */ }
        }
      }
      if (!image) continue // require an image to publish
      resolved.push({ id: base || title, title, summary, url, eyebrow, image, date })
    }
    resolved.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
    runtimeItems.value = resolved
  } catch (_) {
    // ignore — fallback to build-time items
  }
})

const items = computed(() => {
  if (runtimeItems.value && runtimeItems.value.length) return runtimeItems.value
  const result = []
  for (const [path, data] of Object.entries(jsonModules)) {
    const name = path.split('/').pop().replace(/\.json$/i, '')
    // Prefer WebP, fallback to other formats
    const img =
      imageModules[`../news/${name}.webp`] ||
      imageModules[`../news/${name}.jpeg`] ||
      imageModules[`../news/${name}.jpg`] ||
      imageModules[`../news/${name}.png`]
    if (!img) continue

    const title = data.title || data.headline || name
    const summary = data.summary || data.excerpt || ''
    const url = normalizeLink(data.url || data.link || '')
    const eyebrow = data.eyebrow || 'News'
    const date = data.date || data.published || data.publishedAt || data.time || null
    const image = sanitizeSrc(resolveUrl(img))
    if (!image) continue
    result.push({ id: name, title, summary, url, eyebrow, image, date })
  }
  result.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
  return result
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1.2fr .8fr .8fr; gap: 20px; align-items: start; }
.media { position: relative; border-radius: 16px; overflow: hidden; }
.media-img { height: 280px; background: url('https://images.unsplash.com/photo-1511497584788-876760111969?q=80&w=1200&auto=format&fit=crop') center/cover no-repeat; filter: saturate(110%); }
.play { position: absolute; inset: auto auto 16px 16px; border: none; border-radius: 50%; width: 48px; height: 48px; background: rgba(255,255,255,0.9); font-size: 18px; cursor: pointer; }
.note { padding: 18px 18px 16px; border-radius: 14px; }
.note .thumb { width: 100%; height: 90px; object-fit: cover; border-radius: 10px; margin: 8px 0 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); display: block; }
.note.green { background: #D6F1EB; }
.note.yellow { background: #FFE487; }
.more { color: var(--cta-f26a2e); font-weight: 600; }
@media (max-width: 1100px) {
  .grid { grid-template-columns: 1fr; }
  .media-img { height: 220px; }
}
</style>
