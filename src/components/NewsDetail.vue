<template>
  <main v-if="item">
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <div class="eyebrow">News:</div>
          <h1 class="h2-50" v-text="item.title"></h1>
        </div>
        <div>
          <p class="brodtext-20 muted" v-text="item.intro || item.summary || ''" />
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

    <!-- Related posts -->
    <section class="section gradient-sunrise related">
      <div class="container">
        <h3 class="h3-30 section-title">Related posts</h3>
        <div class="cards">
          <article v-for="r in related" :key="r.id" class="card project">
            <div class="img" :style="{ backgroundImage: r.image ? `url(${r.image})` : undefined }"></div>
            <div class="body">
              <h4 class="h3-30" v-text="r.title" />
              <p class="brodtext-20 muted" v-text="r.summary || ''" />
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
import { isValidSlug } from '../utils/sanitize'
import { withBase, resolveUrl } from '../utils/paths.js'
import {
  normalizeImage,
  normalizeVideo,
  normalizeLink,
  normalizePapers,
  parseBodyParagraphs,
  processImages,
  fetchContacts,
  fetchRelatedItems
} from '../utils/detailHelpers'
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
const bodyParas = computed(() => parseBodyParagraphs(item.value?.body))

const detailHref = (slug) => withBase(`news/detail.html?slug=${encodeURIComponent(slug)}`)

onMounted(async () => {
  if (!slug || !isValidSlug(slug)) return
  try {
    const r = await fetch(resolveUrl(`content/news/${slug}.json`), { cache: 'default' })
    if (!r.ok) return
    const data = await r.json()

    const { images: orderedImages, captions: normalizedCaptions, headlineImage } = processImages(data)

    item.value = {
      id: slug,
      title: data.title || slug,
      intro: data.intro || data.summary || '',
      subheading: data.subheading || data.headline || 'Details',
      body: data.body || '',
      image: headlineImage,
      images: orderedImages,
      imageCaptions: normalizedCaptions,
      video: normalizeVideo(data.video || null),
      papers: normalizePapers(data.papers),
      date: data.date || data.published || data.publishedAt || null,
    }

    const relatedSlugs = Array.isArray(data.related) ? data.related : []
    related.value = await fetchRelatedItems(relatedSlugs, 'content/news', 3)

    const contactSlugs = Array.isArray(data.contacts) ? data.contacts : []
    contacts.value = await fetchContacts(contactSlugs, MAX_CONTACTS)
  } catch (_) {}
})
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

.body { padding-top: 24px; padding-bottom: 24px; }
.gallery { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.gallery-card { margin: 0; padding: 12px; border-radius: 12px; background: rgba(242, 243, 249, 0.9); display: flex; flex-direction: column; gap: 8px; }
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
.person { text-align: left; display: flex; flex-direction: column; gap: 6px; }
.avatar { height: 300px; width: 300px; border-radius: 12px; background-size: cover; background-position: center; filter: grayscale(20%); background-color: #e9e9ee; }
.name { font-weight: 600; }
.role { font-size: 14px; }

.related .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.project .img { height: 180px; background: #ddd center/cover no-repeat; }
.project .body { padding: 14px 16px 18px; }
.project a.more { color: var(--cta-f26a2e); font-weight: 600; }
.section-title { text-align: center; margin-bottom: 20px; }
.papers { padding-top: 24px; padding-bottom: 24px; }
.papers-list { margin-top: 12px; padding-left: 22px; list-style: decimal; }
.papers-list li { margin-bottom: 6px; }
.papers-list a { color: var(--cta-f26a2e); font-weight: 600; word-break: break-word; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
  .gallery { grid-template-columns: 1fr; }
  .video-wrap { padding-top: 56.25%; }
  .contacts .people { grid-template-columns: 1fr; }
  .hero-img {
    height: auto;
    max-height: 400px !important; /* Smaller max on mobile */
  }
  .related .cards { grid-template-columns: 1fr; }
  .avatar { height: 200px; width: 200px; }
}
</style>
