<template>
  <main>
    <section class="section gradient-sunrise hero">
      <div class="container hero-inner">
        <div>
          <h1 class="h2-50">Gallery</h1>
          <p class="brodtext-20 muted">
            A visual record of DTCC projects, experiments, and community moments. Items are sourced from the
            repository content folder so new imagery can be published without a code change.
          </p>
          <p class="brodtext-20 muted" v-if="items.length">
            Currently featuring {{ items.length }} highlight{{ items.length === 1 ? '' : 's' }}.
          </p>
        </div>
      </div>
    </section>

    <section class="section gallery">
      <div class="container">
        <div v-if="items.length" class="grid">
          <figure
            v-for="entry in items"
            :key="entry.id"
            class="card tile"
            role="button"
            tabindex="0"
            @click="open(entry)"
            @keydown.enter.prevent="open(entry)"
            @keydown.space.prevent="open(entry)"
          >
            <div class="image" :style="{ backgroundImage: entry.image ? `url(${entry.image})` : undefined }" />
            <figcaption>
              <h3 class="h3-30" v-text="entry.title" />
              <p class="brodtext-20 muted" v-text="entry.description" />
            </figcaption>
          </figure>
        </div>
        <div v-else class="empty">
          <h3 class="h3-30">No gallery items yet</h3>
          <p class="brodtext-20 muted">
            Add JSON entries to <code>public/content/gallery</code> (and optionally matching files in <code>src/gallery</code>)
            to have imagery appear here during build and at runtime.
          </p>
        </div>
      </div>
    </section>

    <div
      v-if="activeItem"
      class="lightbox"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="`gallery-item-${activeItem.id}`"
      @click.self="close"
    >
      <div class="panel">
        <button class="close" type="button" aria-label="Close gallery item" @click="close">×</button>
        <img class="full" :src="activeItem.image" :alt="activeItem.title" />
        <div class="caption">
          <h3 class="h3-30" :id="`gallery-item-${activeItem.id}`" v-text="activeItem.title" />
          <p class="brodtext-20 muted" v-text="activeItem.description" />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { resolveUrl, withBase } from '../utils/paths.js'
import { sanitizeSrc } from '../utils/sanitize.js'

// Build-time fallback content shipped from src/gallery
const jsonModules = import.meta.glob('../gallery/*.json', { eager: true, import: 'default' })
const imageModules = import.meta.glob('../gallery/*.{jpg,jpeg,png,webp,avif}', { eager: true, import: 'default' })

// Runtime content loaded from public/content/gallery
const runtimeItems = ref([])
const activeItem = ref(null)

const normalizeItem = (payload = {}, fallbackId = '') => {
  const id = payload.id || payload.slug || payload.base || fallbackId || payload.title || 'gallery-item'
  const title = payload.title || payload.name || id
  const description = payload.description || payload.summary || payload.caption || ''
  const imageCandidate = payload.image || payload.thumbnail || null
  const image = sanitizeSrc(resolveUrl(imageCandidate))
  return image ? { id, title, description, image } : null
}

const open = (item) => { activeItem.value = item }
const close = () => { activeItem.value = null }

const handleKeydown = (event) => {
  if (event.key === 'Escape') close()
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  try {
    const response = await fetch(withBase('content/gallery/index.json'), { cache: 'default' })
    if (!response.ok) return
    const manifest = await response.json()
    const entries = Array.isArray(manifest?.items)
      ? manifest.items
      : Array.isArray(manifest)
        ? manifest
        : []

    const loaded = []
    for (const entry of entries) {
      const base = (typeof entry === 'string') ? entry : entry.base || entry.id || entry.slug || entry.name
      const initial = typeof entry === 'string' ? {} : entry
      let data = { ...initial }

      if (!data.title || !data.description || !data.image) {
        const jsonPath = data.json || (base ? `content/gallery/${base}.json` : null)
        if (jsonPath) {
          try {
            const r = await fetch(resolveUrl(jsonPath), { cache: 'default' })
            if (r.ok) {
              const extra = await r.json()
              data = { ...extra, ...data }
            }
          } catch (_) {
            /* ignore individual entry errors */
          }
        }
      }

      if (!data.image && base) {
        const extensions = ['avif', 'webp', 'jpeg', 'jpg', 'png']
        for (const ext of extensions) {
          const url = resolveUrl(`content/gallery/${base}.${ext}`)
          try {
            const head = await fetch(url, { method: 'HEAD' })
            if (head.ok) {
              data.image = url
              break
            }
          } catch (_) {
            /* ignore */
          }
        }
      }

      const normalized = normalizeItem(data, base)
      if (normalized) loaded.push(normalized)
    }

    // Preserve manifest order
    runtimeItems.value = loaded
  } catch (_) {
    // fall back to build-time assets
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

const items = computed(() => {
  if (runtimeItems.value.length) return runtimeItems.value

  const fallback = []
  for (const [path, data] of Object.entries(jsonModules)) {
    const base = path.split('/').pop()?.replace(/\.json$/i, '') || ''
    const localImage =
      imageModules[`../gallery/${base}.avif`] ||
      imageModules[`../gallery/${base}.webp`] ||
      imageModules[`../gallery/${base}.jpeg`] ||
      imageModules[`../gallery/${base}.jpg`] ||
      imageModules[`../gallery/${base}.png`]

    const merged = {
      ...data,
      image: data.image || localImage || null,
      id: data.id || data.slug || data.base || base,
    }

    const normalized = normalizeItem(merged, base)
    if (normalized) fallback.push(normalized)
  }

  return fallback
})
</script>

<style scoped>
.hero { min-height: 320px; display: flex; align-items: center; }
.hero-inner { display: flex; flex-direction: column; gap: 12px; }

.gallery .grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 22px;
}

.tile { display: flex; flex-direction: column; overflow: hidden; border-radius: 16px; }
.tile .image {
  position: relative;
  padding-top: 62%;
  background-size: cover;
  background-position: center;
}
.tile figcaption { padding: 18px 20px 20px; display: flex; flex-direction: column; gap: 10px; }
.tile { cursor: pointer; outline: none; }
.tile:focus-visible { box-shadow: 0 0 0 3px rgba(250, 218, 54, 0.65); }

.empty {
  text-align: center;
  padding: 60px 20px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 16px;
}
.empty code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; }

.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 14, 0.75);
  display: grid;
  place-items: center;
  padding: 24px;
  z-index: 50;
}
.panel {
  background: #fff;
  border-radius: 18px;
  max-width: min(960px, 92vw);
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.35);
  position: relative;
}
.close {
  position: absolute;
  top: 12px;
  right: 12px;
  border: none;
  background: rgba(17,17,23,0.7);
  color: #fff;
  font-size: 22px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  cursor: pointer;
}
.close:hover { filter: brightness(1.1); }
.full {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  max-height: 70vh;
}
.caption {
  padding: 20px 24px 24px;
  background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(255,255,255,1) 70%);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

@media (max-width: 720px) {
  .tile figcaption { padding: 16px 16px 18px; }
  .panel { max-height: 92vh; }
  .full { max-height: 58vh; }
}
</style>
