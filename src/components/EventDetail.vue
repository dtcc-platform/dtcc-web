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
        <div class="hero-img card" :style="{ backgroundImage: heroImageStyle }"></div>
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
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sanitizeSrc, sanitizeUrl } from '../utils/sanitize'
import { resolveUrl } from '../utils/paths.js'
import { ensureYouTubeEmbed } from '../utils/video'

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
const item = ref(null)
const heroImageStyle = computed(() => item.value?.image ? `url(${item.value.image})` : undefined)
const videoEmbed = computed(() => item.value?.video || null)
const gallery = computed(() => (item.value?.images || []).slice(1))

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
  return sanitizeSrc(resolveUrl(value))
}

const normalizeVideo = (value) => {
  if (!value) return null
  const embed = ensureYouTubeEmbed(value)
  if (!embed) return null
  return sanitizeSrc(embed)
}

onMounted(async () => {
  if (!slug) return
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
    }
  } catch (_) {}
})
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: start; }
.meta strong { font-weight: 600; }
.hero-img { height: 320px; border-radius: 14px; margin-top: 16px; background: #000 center/cover no-repeat; }

.body { padding-top: 24px; padding-bottom: 24px; }
.gallery { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.gallery-card { height: 240px; border-radius: 12px; background: #000 center/cover no-repeat; }
.video-wrap { position: relative; padding-top: 56.25%; margin-top: 20px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2); }
.video-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .hero-img { height: 220px; }
  .gallery { grid-template-columns: 1fr; }
  .gallery-card { height: 200px; }
  .video-wrap { padding-top: 56.25%; }
}
</style>
