<template>
  <main v-if="item">
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <div class="eyebrow">Project:</div>
          <h1 class="h2-50" v-text="item.title"></h1>
          <div v-if="isAuthenticated && wizardEditHref" class="visit">
            <a class="more" :href="wizardEditHref">Edit project »</a>
          </div>
        </div>
        <div>
          <p class="brodtext-20 muted" v-text="item.intro || item.summary || ''" />
          <div v-if="item.website" class="visit">
            <a class="more" :href="item.website" target="_blank" rel="noopener">Visit website »</a>
          </div>
        </div>
      </div>
      <div v-if="item.headlineImage || item.image" class="container">
        <OptimizedImage
          :src="item.headlineImage || item.image"
          :alt="item.title"
          img-class="hero-img card"
          loading="eager"
        />
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
          <div v-if="galleryItems.length" class="gallery">
            <figure
              v-for="(image, i) in galleryItems"
              :key="`${i}-${image.src}`"
              class="gallery-card"
            >
              <a :href="image.src" target="_blank" rel="noopener">
                <img
                  :src="image.src"
                  :alt="image.caption || `${item.title} image ${i + 2}`"
                  loading="lazy"
                  decoding="async"
                />
              </a>
              <figcaption v-if="image.caption" class="caption">{{ image.caption }}</figcaption>
            </figure>
          </div>
          <div v-if="videoEmbed" class="video-wrap">
            <iframe
              :src="videoEmbed"
              title="YouTube video player"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerpolicy="strict-origin-when-cross-origin"
              allowfullscreen
              loading="lazy"
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
    <section v-if="related.length" class="section gradient-sunrise related">
      <div class="container">
        <h3 class="h3-30 section-title">Related projects</h3>
        <div class="cards">
          <article v-for="r in related" :key="r.id" class="card project">
            <img
              :src="r.image || fallbackImage"
              :alt="r.title"
              class="img"
              loading="lazy"
              decoding="async"
            />
            <div class="body">
              <h4 class="h3-30" v-text="r.title" />
              <p class="brodtext-20 muted" v-text="r.summary || r.description || ''" />
              <a :href="detailHref(r.id)" class="more">Read more »</a>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section v-if="papers.length" class="section papers">
      <div class="container">
        <h3 class="h3-30 section-title">Associated papers</h3>
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
import { ref, onMounted, computed } from 'vue'
import { sanitizeSrc, sanitizeUrl, isValidSlug } from '../utils/sanitize'
import { withBase, resolveUrl, getOptimizedImageUrl } from '../utils/paths.js'
import { ensureYouTubeEmbed } from '../utils/video'
import { usePostSession } from '../utils/postSession'
import OptimizedImage from './OptimizedImage.vue'

const params = new URLSearchParams(location.search)
const slug = params.get('slug')

// Validate slug to prevent path traversal attacks
if (slug && !isValidSlug(slug)) {
  console.error('Invalid slug parameter')
}

const item = ref(null)
const related = ref([])
const contacts = ref([])
const MAX_CONTACTS = 2
const { isAuthenticated } = usePostSession()
const videoEmbed = computed(() => item.value?.video || null)
const galleryItems = computed(() => {
  const images = Array.isArray(item.value?.images) ? item.value.images : []
  const captions = Array.isArray(item.value?.imageCaptions) ? item.value.imageCaptions : []
  return images.slice(1).map((src, index) => ({
    src,
    caption: captions[index + 1] || '',
  }))
})
const papers = computed(() => Array.isArray(item.value?.papers) ? item.value.papers : [])

const bodyParas = computed(() => {
  const body = item.value?.body || ''
  if (!body) return []
  if (Array.isArray(body)) return body
  return String(body).split(/\n\n+/).map(s => s.trim()).filter(Boolean)
})

const detailHref = (slug) => withBase(`projects/detail.html?slug=${encodeURIComponent(slug)}`)
const wizardEditHref = computed(() =>
  slug && isValidSlug(slug) ? withBase(`post/?section=projects&slug=${encodeURIComponent(slug)}`) : ''
)
const fallbackImage = withBase('content/Projects Placeholder.webp')

const normalizeImage = (value) => {
  if (!value) return null
  // Don't convert to WebP here - let OptimizedImage component handle it
  // This preserves the fallback mechanism in the <picture> element
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

const isExternalLink = (value) => /^https?:\/\//i.test(value)

const normalizePapers = (value) => {
  if (!Array.isArray(value)) return []
  return value.map((entry) => normalizeLink(entry)).filter(Boolean)
}

onMounted(async () => {
  if (!slug || !isValidSlug(slug)) return
  try {
    const r = await fetch(resolveUrl(`content/projects/${slug}.json`), { cache: 'default' })
    if (!r.ok) return
    const data = await r.json()
    const orderedImages = []
    const orderedCaptions = []
    const rawCaptions = Array.isArray(data.imageCaptions)
      ? data.imageCaptions.map((entry) => (typeof entry === 'string' ? entry.trim() : ''))
      : []
    if (Array.isArray(data.images)) {
      data.images.forEach((entry, idx) => {
        const normalized = normalizeImage(entry)
        if (normalized && !orderedImages.includes(normalized)) {
          orderedImages.push(normalized)
          orderedCaptions.push(rawCaptions[idx] || '')
        }
      })
    }
    let headlineImage = normalizeImage(data.image || null)
    let headlineCaption = ''
    if (headlineImage) {
      const existingIndex = orderedImages.indexOf(headlineImage)
      if (existingIndex !== -1) {
        headlineCaption = orderedCaptions[existingIndex] || ''
        orderedImages.splice(existingIndex, 1)
        orderedCaptions.splice(existingIndex, 1)
      }
      orderedImages.unshift(headlineImage)
      orderedCaptions.unshift(headlineCaption)
    } else if (orderedImages.length) {
      headlineImage = orderedImages[0]
    }
    const normalizedCaptions = orderedImages.map((_, idx) => orderedCaptions[idx] || '')

    const normalizedDetailLink = normalizeLink(data.url || data.link || '')
    const normalizedWebsite = normalizeLink(
      data.website || data.visitUrl || data.visitURL || ''
    )
    const website = normalizedWebsite || (isExternalLink(normalizedDetailLink) ? normalizedDetailLink : '')

    item.value = {
      id: slug,
      title: data.title || data.name || slug,
      intro: data.intro || data.summary || data.description || '',
      subheading: data.subheading || data.headline || 'Details',
      body: data.body || data.details || '',
      image: headlineImage,
      images: orderedImages,
      imageCaptions: normalizedCaptions,
      video: normalizeVideo(data.video || null),
      url: normalizedDetailLink,
      website,
      date: data.date || data.updated || null,
      papers: normalizePapers(data.papers),
    }
    const relatedSlugs = Array.isArray(data.related) ? data.related.slice(0, 3) : []
    if (relatedSlugs.length) {
      // Fetch all related items in parallel for better performance
      const results = await Promise.all(
        relatedSlugs.map(async (refSlug) => {
          try {
            const refRes = await fetch(resolveUrl(`content/projects/${refSlug}.json`), { cache: 'default' })
            if (!refRes.ok) return null
            const refData = await refRes.json()
            return {
              id: refSlug,
              title: refData.title || refSlug,
              summary: refData.summary || refData.excerpt || refData.description || '',
              image: normalizeImage(refData.image || (Array.isArray(refData.images) ? refData.images[0] : null)),
            }
          } catch (_) {
            return null
          }
        })
      )
      related.value = results.filter(Boolean)
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
    const res = await fetch(resolveUrl('content/users.json'), { cache: 'default' })
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
.hero-img {
  display: block;  /* Ensure block display */
  width: 100%;
  height: auto;  /* Let height be automatic based on aspect ratio */
  max-height: 520px !important;  /* Absolute maximum to prevent overwhelming */
  border-radius: 14px;
  margin-top: 16px;
  object-fit: contain;  /* Show entire image without cropping */
  object-position: center;  /* Center the image */
  background: rgba(242, 243, 249, 0.9);
  padding: 12px;
  box-sizing: border-box;
}
.visit { margin-top: 10px; }

.body { padding-top: 24px; padding-bottom: 24px; }
.gallery { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.gallery-card { margin: 0; padding: 12px; border-radius: 12px; background: rgba(0, 0, 0, 0.05); display: flex; flex-direction: column; gap: 8px; }
.gallery-card a { display: block; border-radius: 10px; overflow: hidden; }
.gallery-card img {
  display: block;
  width: 100%;
  height: auto;
  max-height: 400px;  /* Reasonable maximum height for gallery images */
  border-radius: 10px;
  object-fit: contain;  /* Preserve aspect ratio, show full image */
  background: #050507;
}
.gallery-card .caption { font-size: 0.9rem; color: rgba(26, 26, 31, 0.7); line-height: 1.4; }
.video-wrap { position: relative; padding-top: 56.25%; margin-top: 20px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2); }
.video-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }

.contacts .people { margin-top: 16px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.contacts .person { text-align: left; display: flex; flex-direction: column; gap: 6px; }
.contacts .avatar { height: 300px; width: 300px; border-radius: 12px; background-size: cover; background-position: center; background-color: #e9e9ee; }
.contacts .name { font-weight: 600; }
.contacts .role { font-size: 14px; }

.related .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
  background-color: rgba(242, 243, 249, 0.9);
  border-radius: 14px;
  padding: 8px;
  box-sizing: border-box;
}
.project .body { padding: 14px 16px 18px; }
.project a.more { color: var(--cta-f26a2e); font-weight: 600; }
.section-title { text-align: center; margin-bottom: 20px; }
.papers { padding-top: 24px; padding-bottom: 24px; }
.papers-list { margin-top: 12px; padding-left: 22px; list-style: decimal; }
.papers-list li { margin-bottom: 6px; }
.papers-list a { color: var(--cta-f26a2e); font-weight: 600; word-break: break-word; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .hero-img {
    height: auto;
    max-height: 400px !important; /* Smaller max on mobile */
  }
  .gallery { grid-template-columns: 1fr; }
  .avatar { height: 200px; width: 200px; }
  .video-wrap { padding-top: 56.25%; }
  .contacts .people { grid-template-columns: 1fr; }
  .related .cards { grid-template-columns: 1fr; }
  .papers-list { padding-left: 20px; }
}
</style>
