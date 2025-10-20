<template>
  <main v-if="item">
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <div class="eyebrow">Event:</div>
          <h1 class="h2-50" v-text="item.title" />
        </div>
        <div>
          <p class="brodtext-20 muted" v-text="item.summary || item.intro || ''" />
          <div class="meta brodtext-20">
            <strong>{{ meta }}</strong>
            <template v-if="item.registration">
              · <a class="more" :href="item.registration" target="_blank" rel="noopener">Register »</a>
            </template>
          </div>
        </div>
      </div>
      <div v-if="item.image" class="container">
        <OptimizedImage
          :src="item.image"
          :alt="item.title"
          img-class="hero-img card"
          loading="eager"
        />
      </div>
    </section>

    <section class="section gradient-sunrise body">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Details</h2>
        </div>
        <div>
          <p class="brodtext-20 muted" v-for="(p, i) in bodyParas" :key="i" v-text="p" />
          <div v-if="gallery.length" class="gallery">
            <div
              v-for="(img, i) in gallery"
              :key="`${i}-${img}`"
              class="gallery-card"
              :style="{ backgroundImage: `url(${img})` }"
            ></div>
          </div>
          <div v-if="videoEmbed" class="video-wrap">
            <iframe
              :src="videoEmbed"
              title="YouTube video player"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerpolicy="strict-origin-when-cross-origin"
              allowfullscreen
            ></iframe>
          </div>
        </div>
      </div>
    </section>

    <section v-if="papers.length" class="section papers">
      <div class="container">
        <h3 class="h3-30">Associated papers</h3>
        <ol class="papers-list">
          <li v-for="(paper, index) in papers" :key="`${index}-${paper}`">
            <a :href="paper" target="_blank" rel="noopener">Paper {{ index + 1 }}</a>
          </li>
        </ol>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sanitizeSrc, sanitizeUrl, isValidSlug } from '../utils/sanitize'
import { resolveUrl, getOptimizedImageUrl } from '../utils/paths.js'
import { ensureYouTubeEmbed } from '../utils/video'
import OptimizedImage from './OptimizedImage.vue'

const normalizeLink = (value) => {
  if (!value) return ''
  const trimmed = value.trim()
  if (!trimmed || trimmed === '#') return ''
  const resolved = resolveUrl(trimmed)
  if (typeof resolved !== 'string') return ''
  return resolved.startsWith('/') ? resolved : sanitizeUrl(resolved)
}

const params = new URLSearchParams(location.search)
const slug = params.get('slug')

// Validate slug to prevent path traversal attacks
if (slug && !isValidSlug(slug)) {
  console.error('Invalid slug parameter')
}

const item = ref(null)
const videoEmbed = computed(() => item.value?.video || null)
const gallery = computed(() => (item.value?.images || []).slice(1))
const papers = computed(() => Array.isArray(item.value?.papers) ? item.value.papers : [])

const suffixDay = (n) => {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return s[(v - 20) % 10] || s[v] || s[0]
}

const meta = computed(() => {
  if (!item.value) return ''
  if (item.value.meta) return item.value.meta
  const d = new Date(item.value.date)
  const m = d.toLocaleString(undefined, { month: 'long' })
  const day = d.getDate()
  const start = item.value.timeStart || ''
  const end = item.value.timeEnd || ''
  const time = start && end ? `${start}–${end}` : start || end || ''
  const loc = item.value.location || ''
  return [ `${m} ${day}${suffixDay(day)}`, time, loc ].filter(Boolean).join(', ')
})

const bodyParas = computed(() => {
  const body = item.value?.body || ''
  if (!body) return []
  if (Array.isArray(body)) return body
  return String(body).split(/\n\n+/).map(s => s.trim()).filter(Boolean)
})

const normalizeImage = (value) => {
  if (!value) return null
  const optimized = getOptimizedImageUrl(value)
  return sanitizeSrc(resolveUrl(optimized))
}

const normalizeVideo = (value) => {
  if (!value) return null
  const embed = ensureYouTubeEmbed(value)
  if (!embed) return null
  return sanitizeSrc(embed)
}

onMounted(async () => {
  if (!slug || !isValidSlug(slug)) return
  try {
    const r = await fetch(resolveUrl(`content/events/${slug}.json`), { cache: 'no-store' })
    if (!r.ok) return
    const data = await r.json()
    const orderedImages = []
    if (Array.isArray(data.images)) {
      for (const entry of data.images) {
        const normalized = normalizeImage(entry)
        if (normalized && !orderedImages.includes(normalized)) {
          orderedImages.push(normalized)
        }
      }
    }
    let headlineImage = normalizeImage(data.image || null)
    if (headlineImage) {
      const existingIndex = orderedImages.indexOf(headlineImage)
      if (existingIndex !== -1) {
        orderedImages.splice(existingIndex, 1)
      }
      orderedImages.unshift(headlineImage)
    } else if (orderedImages.length) {
      headlineImage = orderedImages[0]
    }

    item.value = {
      id: slug,
      title: data.title || slug,
      summary: data.summary || data.description || '',
      body: data.body || '',
      image: headlineImage,
      images: orderedImages,
      video: normalizeVideo(data.video || null),
      date: data.date || null,
      timeStart: data.timeStart || null,
      timeEnd: data.timeEnd || null,
      location: data.location || null,
      meta: data.meta || null,
      registration: normalizeLink(data.registration || ''),
      papers: Array.isArray(data.papers) ? data.papers.map((entry) => normalizeLink(entry)).filter(Boolean) : [],
    }
  } catch (_) {}
})
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: start; }
.meta strong { font-weight: 600; }
.hero-img { width: 100%; height: 320px; border-radius: 14px; margin-top: 16px; object-fit: cover; background: #000; }

.body { padding-top: 24px; padding-bottom: 24px; }
.gallery { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.gallery-card { height: 240px; border-radius: 12px; background: #000 center/cover no-repeat; }
.video-wrap { position: relative; padding-top: 56.25%; margin-top: 20px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2); }
.video-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.papers { padding-top: 24px; padding-bottom: 24px; }
.papers-list { margin-top: 12px; padding-left: 22px; list-style: decimal; }
.papers-list li { margin-bottom: 6px; }
.papers-list a { color: var(--cta-f26a2e); font-weight: 600; word-break: break-word; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .hero-img { height: 220px; }
  .gallery { grid-template-columns: 1fr; }
  .gallery-card { height: 200px; }
  .video-wrap { padding-top: 56.25%; }
  .papers-list { padding-left: 20px; }
}
</style>
