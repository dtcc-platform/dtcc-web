<template>
  <section id="projects" class="section">
    <div class="container">
      <h3 class="h3-30 section-title">Latest projects</h3>
      <div class="cards">
        <template v-if="items.length">
          <article v-for="p in items" :key="p.id" class="card project">
            <div
              :class="['img', { 'no-image': !p.hasImage }]"
              :style="{ backgroundImage: p.hasImage ? `url(${p.image})` : undefined }"
            ></div>
            <div class="body">
              <h4 class="h3-30" v-text="p.title" />
              <p class="brodtext-20 muted" v-text="p.summary || p.excerpt || p.description" />
              <a :href="p.url || p.link || '#'">Read more »</a>
            </div>
          </article>
        </template>
        <template v-else>
          <article class="card project">
            <div class="img" style="background-image:url('https://images.unsplash.com/photo-1494516192674-b82b5f1e61dc?q=80&w=1200&auto=format&fit=crop')"></div>
            <div class="body">
              <h4 class="h3-30">Urban Environmental Comfort Design</h4>
              <p class="brodtext-20 muted">Urban densification influences wind, temperature, noise, daylight and air quality at both city scale and ...</p>
              <a href="#">Read more »</a>
            </div>
          </article>
          <article class="card project">
            <div class="img" style="background-image:url('https://images.unsplash.com/photo-1518306727298-4c17e1bf6942?q=80&w=1200&auto=format&fit=crop')"></div>
            <div class="body">
              <h4 class="h3-30">4D digital twin for underground, and natural hazards</h4>
              <p class="brodtext-20 muted">Developing decision support systems to help making informed decisions ...</p>
              <a href="#">Read more »</a>
            </div>
          </article>
          <article class="card project">
            <div class="img" style="background-image:url('https://images.unsplash.com/photo-1517153295259-74eb0b401b47?q=80&w=1200&auto=format&fit=crop')"></div>
            <div class="body">
              <h4 class="h3-30">Mobility and the liveable city</h4>
              <p class="brodtext-20 muted">A city-scale twin helps us test street redesigns, public realm and network impacts ...</p>
              <a href="#">Read more »</a>
            </div>
          </article>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { sanitizeUrl, sanitizeSrc } from '../utils/sanitize'
import { withBase, resolveUrl } from '../utils/paths.js'

// Build-time source from src/projects
const jsonModules = import.meta.glob('../projects/*.json', { eager: true, import: 'default' })
const imageModules = import.meta.glob('../projects/*.{jpg,jpeg,png}', { eager: true, import: 'default' })

// Runtime source from public/projects
const runtimeItems = ref([])

const normalizeImage = (value) => {
  if (!value) return null
  return sanitizeSrc(resolveUrl(value))
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
    const idx = await fetch(withBase('content/projects/index.json'), { cache: 'no-store' })
    if (!idx.ok) return
    const payload = await idx.json()
    const arr = Array.isArray(payload.items) ? payload.items : Array.isArray(payload) ? payload : []
    const bases = arr.map((it) => (typeof it === 'string' ? { base: it } : it))
    const resolved = []
    for (const it of bases) {
      const base = it.base || it.name || it.file || it.id
      const jsonPath = it.json || (base ? `content/projects/${base}.json` : null)
      let data = {}
      if (jsonPath) {
        try {
          const r = await fetch(resolveUrl(jsonPath), { cache: 'no-store' })
          if (r.ok) data = await r.json()
        } catch (_) {}
      }
      const title = it.title || data.title || data.name || base || 'Untitled project'
      const summary = it.summary || data.summary || data.excerpt || data.description || ''
      const url = normalizeLink(it.url || data.url || data.link || '')
      const date = it.date || data.date || data.published || data.updated || null
      const image = normalizeImage(it.image || data.image || null)
      resolved.push({ id: base || title, title, summary, url, image, hasImage: Boolean(image), date })
    }
    resolved.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
    runtimeItems.value = resolved
  } catch (_) {}
})

const items = computed(() => {
  if (runtimeItems.value && runtimeItems.value.length) return runtimeItems.value
  const result = []
  for (const [path, data] of Object.entries(jsonModules)) {
    const name = path.split('/').pop().replace(/\.json$/i, '')
    const img =
      imageModules[`../projects/${name}.jpeg`] ||
      imageModules[`../projects/${name}.jpg`] ||
      imageModules[`../projects/${name}.png`]
    const title = data.title || data.name || name
    const summary = data.summary || data.excerpt || data.description || ''
    const url = normalizeLink(data.url || data.link || '')
    const date = data.date || data.published || data.updated || null
    const image = img ? sanitizeSrc(resolveUrl(img)) : null
    result.push({ id: name, title, summary, url, image, hasImage: Boolean(image), date })
  }
  result.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
  return result
})
</script>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.project .img { height: 180px; background: #ddd center/cover no-repeat; }
.project .img.no-image {
  background: #f3f3f3;
  color: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.project .img.no-image::after {
  content: 'No image';
}
.project .body { padding: 14px 16px 18px; }
.project a { color: var(--cta-f26a2e); font-weight: 600; }
@media (max-width: 1100px) { .cards { grid-template-columns: 1fr 1fr; } }
@media (max-width: 700px) { .cards { grid-template-columns: 1fr; } }
</style>

<style scoped>
.section-title { text-align: center; margin-bottom: 20px; }
</style>
