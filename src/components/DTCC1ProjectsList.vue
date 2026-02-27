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
          <article v-for="p in items" :key="p.id" class="card project">
            <a :href="detailHref(p.id)">
              <img
                :src="p.image || fallbackImage"
                :alt="p.title"
                class="img"
                loading="lazy"
                decoding="async"
              />
            </a>
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
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { sanitizeSrc } from '../utils/sanitize'
import { withBase, resolveUrl } from '../utils/paths.js'
import { usePostSession } from '../utils/postSession'
import { normalizeImage, normalizeLink } from '../utils/detailHelpers'

// Build-time fallback from src/dtcc-1
const jsonModules = import.meta.glob('../dtcc-1/*.json', { eager: true, import: 'default' })
const imageModules = import.meta.glob('../dtcc-1/*.{jpg,jpeg,png,webp}', { eager: true, import: 'default' })

// Runtime source from public/content/dtcc-1
const runtimeItems = ref([])
const { isAuthenticated } = usePostSession()

// List-specific link normalizer (returns '#' instead of empty string)
const normalizeLinkForList = (value) => {
  const result = normalizeLink(value)
  return result || '#'
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
      const url = normalizeLinkForList(it.url || data.url || data.link || '')
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
    const url = normalizeLinkForList(data.url || data.link || '')
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

const detailHref = (slug) => withBase(`dtcc-1/detail.html?slug=${encodeURIComponent(slug)}`)
const editHref = (slug) => withBase(`post/?section=events-archive&slug=${encodeURIComponent(slug)}`)
const fallbackImage = withBase('content/Projects Placeholder.webp')
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .8fr 1.2fr; gap: 28px; align-items: start; }
.links { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
.more { color: var(--cta-f26a2e); font-weight: 600; }

.list .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img { width: 100%; height: 200px; object-fit: cover; display: block; background: #ddd; border-radius: 14px; }
.project .body { padding: 14px 16px 18px; }


@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .list .cards { grid-template-columns: 1fr; }
}
</style>
