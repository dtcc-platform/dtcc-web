<template>
  <main>
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h2-50">DTCC1 Projects:<br>Our first five years</h1>
        </div>
        <div>
          <p class="brodtext-20 muted">
            These are the research projects from DTCC's first phase (2020-2025). During this period, we established the foundation for digital twin technology in Sweden, developed core platforms and tools, and built strong partnerships across academia, industry, and the public sector.
          </p>
        </div>
      </div>
    </section>

    <section class="section gradient-sunrise list">
      <div class="container">
        <div class="cards">
          <article v-for="p in visibleItems" :key="p.id" class="card project">
            <img
              v-if="p.hasImage"
              :src="p.image"
              :alt="p.title"
              class="img"
              loading="lazy"
              decoding="async"
            />
            <div v-else class="img no-image"></div>
            <div class="body">
              <h4 class="h3-30" v-text="p.title" />
              <p class="brodtext-20 muted" v-text="p.description || p.summary || p.excerpt" />
              <a :href="detailHref(p.id)" class="more">Read more »</a>
            </div>
          </article>
        </div>
        <div v-if="items.length > visibleCount" class="more-wrap">
          <button class="btn-more" @click="showMore">Load more</button>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { sanitizeUrl, sanitizeSrc } from '../utils/sanitize'
import { withBase, resolveUrl, getOptimizedImageUrl } from '../utils/paths.js'

// Build-time fallback from src/dtcc-1
const jsonModules = import.meta.glob('../dtcc-1/*.json', { eager: true, import: 'default' })
const imageModules = import.meta.glob('../dtcc-1/*.{jpg,jpeg,png,webp}', { eager: true, import: 'default' })

// Runtime source from public/content/dtcc-1
const runtimeItems = ref([])
const visibleCount = ref(4)
const showMore = () => { visibleCount.value = Math.min(visibleCount.value + 4, items.value.length) }

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
    const idx = await fetch(withBase('content/dtcc-1/index.json'), { cache: 'default' })
    if (!idx.ok) return
    const payload = await idx.json()
    const arr = Array.isArray(payload.items) ? payload.items : Array.isArray(payload) ? payload : []
    const bases = arr.map((it) => (typeof it === 'string' ? { base: it } : it))
    const resolved = []
    for (const it of bases) {
      const base = it.base || it.name || it.file || it.id
      const jsonPath = it.json || (base ? `content/dtcc-1/${base}.json` : null)
      let data = {}
      if (jsonPath) {
        try {
          const r = await fetch(resolveUrl(jsonPath), { cache: 'default' })
          if (r.ok) data = await r.json()
        } catch (_) {}
      }
      const title = it.title || data.title || data.name || base || 'Untitled project'
      const description = it.description || data.description || data.summary || data.excerpt || ''
      const url = normalizeLink(it.url || data.url || data.link || '')
      const date = it.date || data.date || data.published || data.updated || null
      const order = Number.isFinite(Number(it.order)) ? Number(it.order) : (Number.isFinite(Number(data.order)) ? Number(data.order) : undefined)
      const image = normalizeImage(
        it.image ||
        data.image ||
        (Array.isArray(data.images) ? data.images[0] : null)
      )
      resolved.push({ id: base || title, title, description, url, image, hasImage: Boolean(image), date, order })
    }
    // Respect explicit order if provided; otherwise keep manifest order
    if (resolved.some(x => Number.isFinite(x.order))) {
      resolved.sort((a, b) => (a.order ?? 1e9) - (b.order ?? 1e9))
    }
    runtimeItems.value = resolved
  } catch (_) {}
})

const items = computed(() => {
  if (runtimeItems.value && runtimeItems.value.length) return runtimeItems.value
  const result = []
  for (const [path, data] of Object.entries(jsonModules)) {
    const name = path.split('/').pop().replace(/\.json$/i, '')
    const img =
      imageModules[`../dtcc-1/${name}.jpeg`] ||
      imageModules[`../dtcc-1/${name}.jpg`] ||
      imageModules[`../dtcc-1/${name}.png`]
    const remoteImage = normalizeImage(data.image || (Array.isArray(data.images) ? data.images[0] : null))
    const image = img ? sanitizeSrc(resolveUrl(img)) : remoteImage
    const title = data.title || data.name || name
    const description = data.description || data.summary || data.excerpt || ''
    const url = normalizeLink(data.url || data.link || '')
    const date = data.date || data.published || data.updated || null
    const order = Number.isFinite(Number(data.order)) ? Number(data.order) : undefined
    result.push({ id: name, title, description, url, image, hasImage: Boolean(image), date, order })
  }
  if (result.some(x => Number.isFinite(x.order))) {
    result.sort((a, b) => (a.order ?? 1e9) - (b.order ?? 1e9))
  } else {
    // fallback: newest first
    result.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
  }
  return result
})

const detailHref = (slug) => withBase(`projects/detail.html?slug=${encodeURIComponent(slug)}`)
const visibleItems = computed(() => items.value.slice(0, visibleCount.value))
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .8fr 1.2fr; gap: 28px; align-items: start; }
.more { color: var(--cta-f26a2e); font-weight: 600; }

.list .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img { width: 100%; height: 200px; object-fit: cover; display: block; background: #ddd; border-radius: 14px; }
.project .img.no-image {
  background: #f3f3f3;
  color: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.project .img.no-image::after {
  content: 'No image';
}
.project .body { padding: 14px 16px 18px; }

.more-wrap { text-align: center; margin-top: 12px; }
.btn-more { background: var(--cta-f26a2e); color: #fff; border: 0; border-radius: 8px; padding: 10px 16px; font-weight: 600; cursor: pointer; }
.btn-more:hover { filter: brightness(1.05); }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .list .cards { grid-template-columns: 1fr; }
}
</style>
