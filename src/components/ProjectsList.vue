<template>
  <main>
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h2-50">Projects landing:<br>Our latest projects</h1>
        </div>
        <div>
          <p class="brodtext-20 muted">
            Our research projects are a major part of DTCC and where a lot of the work happens. In the coming years, our focus as a centre will be on projects that push the boundaries of what digital twins can do for cities and citizens. This includes developing advanced methods for urban planning and design, exploring sustainable construction processes, using AI to transform how we manage data, and creating powerful tools for modelling, simulation, visualization, and much more. To learn about the projects from our first five years of research, <a class="more" :href="dtcc1Href">click here »</a>
          </p>
        </div>
      </div>
    </section>

    <section class="section gradient-sunrise list">
      <div class="container">
        <div class="cards">
          <article v-for="p in visibleItems" :key="p.id" class="card project">
            <img
              :src="p.image || fallbackImage"
              :alt="p.title"
              class="img"
              loading="lazy"
              decoding="async"
            />
            <div class="body">
              <h4 class="h3-30" v-text="p.title" />
              <p class="brodtext-20 muted" v-text="p.description || p.summary || p.excerpt" />
              <div class="links">
                <a :href="detailHref(p.id)" class="more">Read more »</a>
                <a
                  v-if="isAuthenticated"
                  :href="editHref(p.id)"
                  class="more edit-link"
                >
                  Edit project »
                </a>
              </div>
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
import { usePostSession } from '../utils/postSession'

// Build-time fallback from src/projects
const jsonModules = import.meta.glob('../projects/*.json', { eager: true, import: 'default' })
const imageModules = import.meta.glob('../projects/*.{jpg,jpeg,png,webp}', { eager: true, import: 'default' })

// Runtime source from public/content/projects
const runtimeItems = ref([])
const visibleCount = ref(4)
const showMore = () => { visibleCount.value = Math.min(visibleCount.value + 4, items.value.length) }
const { isAuthenticated } = usePostSession()

const normalizeImage = (value) => {
  if (!value) return null
  // Don't convert to WebP here - let OptimizedImage component handle it
  // This preserves the fallback mechanism in the <picture> element
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
    const idx = await fetch(withBase('content/projects/index.json'), { cache: 'default' })
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
      imageModules[`../projects/${name}.jpeg`] ||
      imageModules[`../projects/${name}.jpg`] ||
      imageModules[`../projects/${name}.png`]
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
const editHref = (slug) => withBase(`post/?section=projects&slug=${encodeURIComponent(slug)}`)
const dtcc1Href = withBase('dtcc-1/')
const fallbackImage = withBase('content/Projects Placeholder.webp')
const visibleItems = computed(() => items.value.slice(0, visibleCount.value))
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .8fr 1.2fr; gap: 28px; align-items: start; }
.links { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
.more { color: var(--cta-f26a2e); font-weight: 600; }

.list .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
  background-color: rgba(242, 243, 249, 0.9);
  border-radius: 14px;
  padding: 8px;
  box-sizing: border-box;
}
.project .body { padding: 14px 16px 18px; }
.edit-link { opacity: 0.85; }

.more-wrap { text-align: center; margin-top: 12px; }
.btn-more { background: var(--cta-f26a2e); color: #fff; border: 0; border-radius: 8px; padding: 10px 16px; font-weight: 600; cursor: pointer; }
.btn-more:hover { filter: brightness(1.05); }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .list .cards { grid-template-columns: 1fr; }
}
</style>
