<template>
  <section id="news" class="section">
    <div class="container">
      <h3 class="h3-30 section-title">Latest news</h3>
      <div class="cards">
        <template v-if="items.length">
          <article v-for="n in items" :key="n.id" class="card news-item">
            <a :href="n.url || n.link || '#'">
              <img
                :src="n.previewImage || n.image || fallbackImage"
                :alt="n.title"
                class="img"
                loading="lazy"
                decoding="async"
              />
            </a>
            <div class="body">
              <h4 class="h3-30" v-text="n.title" />
              <p class="brodtext-20 muted" v-text="n.summary || n.excerpt || n.description" />
              <a :href="n.url || n.link || '#'">Read more »</a>
            </div>
          </article>
        </template>
        <template v-else>
          <article class="card news-item">
            <div
              class="img placeholder"
              style="background-image:url('https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1200&auto=format&fit=crop')"
            ></div>
            <div class="body">
              <h4 class="h3-30">Create tool webinar - Join us on June 12th</h4>
              <p class="brodtext-20 muted">Years of collaboration, research, and co-creation with cities across Europe, we're excited to ...</p>
              <a href="#">Read more »</a>
            </div>
          </article>
          <article class="card news-item">
            <div
              class="img placeholder"
              style="background-image:url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1200&auto=format&fit=crop')"
            ></div>
            <div class="body">
              <h4 class="h3-30">DTCC kicks off 5-year extension in 2025</h4>
              <p class="brodtext-20 muted">The Digital Twin Cities Centre (DTCC) is set to embark on its next phase, with a five-year extension approved by ...</p>
              <a href="#">Read more »</a>
            </div>
          </article>
          <article class="card news-item">
            <div
              class="img placeholder"
              style="background-image:url('https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=1200&auto=format&fit=crop')"
            ></div>
            <div class="body">
              <h4 class="h3-30">New partnership with European cities announced</h4>
              <p class="brodtext-20 muted">DTCC expands its network with new collaborations across multiple European urban centers ...</p>
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
import { withBase, resolveUrl, getOptimizedImageUrl } from '../utils/paths.js'

// Build-time source from src/news
const jsonModules = import.meta.glob('../news/*.json', { eager: true, import: 'default' })
const imageModules = import.meta.glob('../news/*.{jpg,jpeg,png,webp}', { eager: true, import: 'default' })

// Runtime source from public/news
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
    const idx = await fetch(withBase('content/news/index.json'), { cache: 'default' })
    if (!idx.ok) return
    const payload = await idx.json()
    const arr = Array.isArray(payload.items) ? payload.items : Array.isArray(payload) ? payload : []
    const bases = arr.map((it) => (typeof it === 'string' ? { base: it } : it))
    const resolved = []
    for (const it of bases) {
      const base = it.base || it.name || it.file || it.id
      const jsonPath = it.json || (base ? `content/news/${base}.json` : null)
      let data = {}
      if (jsonPath) {
        try {
          const r = await fetch(resolveUrl(jsonPath), { cache: 'default' })
          if (r.ok) data = await r.json()
        } catch (_) {}
      }
      const title = it.title || data.title || data.headline || base || 'Untitled'
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
    // Prefer WebP, fallback to other formats
    const img =
      imageModules[`../news/${name}.webp`] ||
      imageModules[`../news/${name}.jpeg`] ||
      imageModules[`../news/${name}.jpg`] ||
      imageModules[`../news/${name}.png`]
    const title = data.title || data.headline || name
    const summary = data.summary || data.excerpt || data.description || ''
    const url = normalizeLink(data.url || data.link || '')
    const date = data.date || data.published || data.updated || null
    const image = img ? sanitizeSrc(resolveUrl(img)) : null
    result.push({ id: name, title, summary, url, image, hasImage: Boolean(image), date })
  }
  result.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
  return result
})

const fallbackImage = withBase('content/News Placeholder.webp')
</script>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.news-item .img {
  width: 100%;
  height: 180px;
  display: block;
  object-fit: cover;
  background-color: rgba(242, 243, 249, 0.9);
  border-radius: 14px;
  padding: 8px;
  box-sizing: border-box;
}
.news-item .img.placeholder {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.news-item .body { padding: 14px 16px 18px; }
.news-item a { color: var(--cta-f26a2e); font-weight: 600; }
@media (max-width: 1100px) { .cards { grid-template-columns: 1fr 1fr; } }
@media (max-width: 700px) { .cards { grid-template-columns: 1fr; } }
</style>

<style scoped>
.section-title { text-align: left; margin-bottom: 20px; }
</style>
