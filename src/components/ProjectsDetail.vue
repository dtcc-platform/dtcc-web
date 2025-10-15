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
      <div v-if="item.image" class="container">
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
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </div>
      </div>
    </section>

    <!-- Contacts -->
    <section v-if="contacts.length" class="section contacts">
      <div class="container">
        <h3 class="h3-30">Contacts</h3>
        <div class="people">
          <div class="person" v-for="c in contacts" :key="c.id">
            <div v-if="c.image" class="avatar" :style="{ backgroundImage: c.image ? `url(${c.image})` : undefined }"></div>
            <div class="name" v-text="c.name" />
            <div v-if="c.title" class="role muted" v-text="c.title" />
            <a v-if="c.email" :href="`mailto:${c.email}`" class="more">Email »</a>
          </div>
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
import { ensureYouTubeEmbed } from '../utils/video'

const params = new URLSearchParams(location.search)
const slug = params.get('slug')
const item = ref(null)
const related = ref([])
const contacts = ref([])
const MAX_CONTACTS = 2
const heroImageStyle = computed(() => item.value?.image ? `url(${item.value.image})` : undefined)
const videoEmbed = computed(() => item.value?.video || null)
const gallery = computed(() => (item.value?.images || []).slice(1))

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

const normalizeVideo = (value) => {
  if (!value) return null
  const embed = ensureYouTubeEmbed(value)
  if (!embed) return null
  return sanitizeSrc(embed)
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
      title: data.title || data.name || slug,
      intro: data.intro || data.summary || data.description || '',
      subheading: data.subheading || data.headline || 'Details',
      body: data.body || data.details || '',
      image: headlineImage,
      images: orderedImages,
      video: normalizeVideo(data.video || null),
      url: normalizeLink(data.url || data.link || ''),
      date: data.date || data.updated || null,
    }
    const relatedSlugs = Array.isArray(data.related) ? data.related.slice(0, 3) : []
    if (relatedSlugs.length) {
      const entries = []
      for (const refSlug of relatedSlugs) {
        try {
          const refRes = await fetch(resolveUrl(`content/projects/${refSlug}.json`), { cache: 'no-store' })
          if (!refRes.ok) continue
          const refData = await refRes.json()
          entries.push({
            id: refSlug,
            title: refData.title || refSlug,
            summary: refData.summary || refData.excerpt || refData.description || '',
            image: normalizeImage(refData.image || (Array.isArray(refData.images) ? refData.images[0] : null)),
          })
        } catch (_) {}
      }
      related.value = entries
    } else {
      related.value = []
    }

    const contactSlugs = Array.isArray(data.contacts) ? data.contacts.slice(0, MAX_CONTACTS) : []
    if (contactSlugs.length) {
      const userMap = await loadUsersMap()
      const entries = contactSlugs.map((refSlug) => {
        const user = userMap[refSlug]
        if (!user) return null
        return {
          id: refSlug,
          name: user.name || user.displayName || refSlug,
          email: user.email || '',
          title: user.title || user.role || '',
          image: normalizeImage(user.photo || user.image || null),
        }
      }).filter(Boolean)
      contacts.value = entries
    } else {
      contacts.value = []
    }
  } catch (_) {}
})

let usersCache = null
async function loadUsersMap() {
  if (usersCache) return usersCache
  try {
    const res = await fetch(resolveUrl('content/users.json'), { cache: 'no-store' })
    if (!res.ok) {
      usersCache = {}
      return usersCache
    }
    const payload = await res.json()
    const items = Array.isArray(payload?.users) ? payload.users : Array.isArray(payload) ? payload : []
    const map = {}
    for (const entry of items) {
      if (!entry) continue
      const key = entry.slug || entry.id || entry.username || entry.email
      if (!key) continue
      map[key] = entry
    }
    usersCache = map
    return usersCache
  } catch (_) {
    usersCache = {}
    return usersCache
  }
}
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: center; }
.hero-img { height: 380px; border-radius: 14px; margin-top: 16px; background: #000 center/cover no-repeat; }
.visit { margin-top: 10px; }

.body { padding-top: 24px; padding-bottom: 24px; }
.gallery { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.gallery-card { height: 260px; border-radius: 12px; background: #000 center/cover no-repeat; }
.video-wrap { position: relative; padding-top: 56.25%; margin-top: 20px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2); }
.video-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }

.contacts .people { margin-top: 16px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.contacts .person { text-align: left; display: flex; flex-direction: column; gap: 6px; }
.contacts .avatar { height: 160px; border-radius: 12px; background-size: cover; background-position: center; background-color: #e9e9ee; }
.contacts .name { font-weight: 600; }
.contacts .role { font-size: 14px; }

.related .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img { height: 180px; background: #ddd center/cover no-repeat; }
.project .body { padding: 14px 16px 18px; }
.project a.more { color: var(--cta-f26a2e); font-weight: 600; }
.section-title { text-align: center; margin-bottom: 20px; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .hero-img { height: 240px; }
  .gallery { grid-template-columns: 1fr; }
  .gallery-card { height: 220px; }
  .video-wrap { padding-top: 56.25%; }
  .contacts .people { grid-template-columns: 1fr; }
  .related .cards { grid-template-columns: 1fr; }
}
</style>
