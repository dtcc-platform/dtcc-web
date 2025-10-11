<template>
  <main>
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h2-50">News landing:<br>Our latest and oldest news</h1>
        </div>
        <div>
          <p class="brodtext-20 muted">
            Placeholder news description text. Use this area to summarise what readers can expect to find here, from the most recent announcements to earlier articles that remain relevant.
          </p>
        </div>
      </div>
    </section>

    <section class="section gradient-sunrise list">
      <div class="container">
        <div class="cards">
          <article v-for="n in visibleItems" :key="n.id" class="card project">
            <div
              :class="['img', { 'no-image': !n.hasImage }]"
              :style="{ backgroundImage: n.hasImage ? `url(${n.image})` : undefined }"
            ></div>
            <div class="body">
              <h4 class="h3-30" v-text="n.title" />
              <p class="brodtext-20 muted" v-text="n.summary || n.excerpt || n.description" />
              <a :href="detailHref(n.id)" class="more">Read more »</a>
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
import { sanitizeSrc } from '../utils/sanitize'
import { withBase, resolveUrl } from '../utils/paths.js'

const runtimeItems = ref([])
const visibleCount = ref(4)
const showMore = () => { visibleCount.value = Math.min(visibleCount.value + 4, items.value.length) }

const normalizeImage = (value) => {
  if (!value) return null
  return sanitizeSrc(resolveUrl(value))
}

onMounted(async () => {
  try {
    const idx = await fetch(withBase('content/news/index.json'), { cache: 'no-store' })
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
          const r = await fetch(resolveUrl(jsonPath), { cache: 'no-store' })
          if (r.ok) data = await r.json()
        } catch (_) {}
      }
      const title = data.title || base
      const summary = data.summary || data.excerpt || data.description || ''
      const image = normalizeImage(it.image || data.image || null)
      const date = data.date || data.published || data.publishedAt || null
      const order = Number.isFinite(Number(it.order)) ? Number(it.order) : Number.isFinite(Number(data.order)) ? Number(data.order) : undefined
      resolved.push({ id: base, title, summary, image, hasImage: Boolean(image), date, order })
    }
    // Sort newest first unless explicit order is provided
    if (resolved.some(x => Number.isFinite(x.order))) {
      resolved.sort((a, b) => (a.order ?? 1e9) - (b.order ?? 1e9))
    } else {
      resolved.sort((a, b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0))
    }
    runtimeItems.value = resolved
  } catch (_) {}
})

const items = computed(() => runtimeItems.value)
const detailHref = (slug) => withBase(`news/detail.html?slug=${encodeURIComponent(slug)}`)
const visibleItems = computed(() => items.value.slice(0, visibleCount.value))
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .8fr 1.2fr; gap: 28px; align-items: start; }
.list .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img { height: 200px; background: #ddd center/cover no-repeat; border-radius: 14px; }
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
