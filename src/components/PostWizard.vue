<template>
  <div class="wizard-shell container">
    <section class="wizard card">
      <header class="wizard-header">
        <p class="eyebrow">Internal tool</p>
        <h1>Post Wizard</h1>
        <p class="muted">
          Draft runtime content directly in the browser. Pick a post type, fill in the fields, review the
          output, and save it into <code>public/content/&lt;type&gt;</code> when you are ready.
        </p>
      </header>

      <form class="wizard-form" @submit.prevent="prepareDraft">
        <fieldset class="field type-fieldset">
          <legend>Post type</legend>
          <div class="type-options">
            <label v-for="option in typeOptions" :key="option.value">
              <input type="radio" :value="option.value" v-model="postType">
              {{ option.label }}
            </label>
          </div>
          <p class="muted helper">Determines where the files are stored under <code>public/content/</code>.</p>
        </fieldset>

        <div class="field">
          <label for="headline">Title<span aria-hidden="true">*</span></label>
          <input
            id="headline"
            v-model="title"
            type="text"
            placeholder="DTCC announces…"
            autocomplete="off"
            required
          >
        </div>

        <div class="field">
          <label for="slug">Slug</label>
          <input
            id="slug"
            v-model="slug"
            type="text"
            autocomplete="off"
            @input="slugWasEdited = true"
          >
          <p class="muted helper">Used for filenames and URLs (e.g. /news/&lt;slug&gt;).</p>
        </div>

        <div class="field">
          <label for="body">Body<span aria-hidden="true">*</span></label>
          <textarea
            id="body"
            v-model="bodyInput"
            rows="6"
            placeholder="Write the post body. Use blank lines to separate paragraphs."
            required
          ></textarea>
        </div>

        <div class="field">
          <label for="post-date">Date<span aria-hidden="true">*</span></label>
          <input
            id="post-date"
            v-model="selectedDate"
            type="date"
            required
          >
          <p class="muted helper">Used for sorting and display. Defaults to today's date.</p>
        </div>

        <div v-if="postType !== 'events'" class="field selection-field">
          <label>Related {{ postType === 'projects' ? 'projects' : 'news items' }}</label>
          <p class="muted helper">Select up to {{ MAX_RELATED }} related entries to feature alongside this post.</p>
          <div v-if="relatedLoading" class="muted helper">Loading related options…</div>
          <div v-else-if="relatedError" class="alert error">{{ relatedError }}</div>
          <div v-else class="selection-list">
            <label v-for="option in relatedOptions" :key="option.slug" class="selection-option">
              <input
                type="checkbox"
                :checked="isRelatedSelected(option.slug)"
                :disabled="!isRelatedSelected(option.slug) && relatedSelectionFull"
                @change="toggleRelated(option.slug, $event.target.checked)"
              >
              <span class="option-text">{{ option.title }}</span>
            </label>
            <p v-if="!relatedOptions.length" class="muted helper">No existing entries available yet.</p>
          </div>
        </div>

        <div v-if="postType !== 'events'" class="field selection-field">
          <label>Contacts</label>
          <p class="muted helper">Pick up to {{ MAX_CONTACTS }} contacts for this {{ postType === 'projects' ? 'project' : 'news item' }}.</p>
          <div v-if="contactLoading" class="muted helper">Loading contacts…</div>
          <div v-else-if="contactError" class="alert error">{{ contactError }}</div>
          <div v-else class="selection-list">
            <label v-for="option in contactOptions" :key="option.slug" class="selection-option">
              <input
                type="checkbox"
                :checked="isContactSelected(option.slug)"
                :disabled="!isContactSelected(option.slug) && contactSelectionFull"
                @change="toggleContact(option.slug, $event.target.checked)"
              >
              <span class="option-text">
                <strong>{{ option.name }}</strong>
                <span v-if="option.email" class="muted small">{{ option.email }}</span>
              </span>
            </label>
            <p v-if="!contactOptions.length" class="muted helper">No contacts available yet.</p>
          </div>
        </div>

        <fieldset class="field image-fieldset">
          <legend>Images</legend>

          <div v-for="(image, index) in imageEntries" :key="image.id" class="image-entry">
            <div class="image-entry-header">
              <span class="image-entry-title">
                {{ index === 0 ? 'Headline image' : `Additional image ${index}` }}
              </span>
              <button
                v-if="index > 0"
                type="button"
                class="btn-icon"
                aria-label="Remove image"
                @click="removeImageEntry(index)"
              >
                ×
              </button>
            </div>

            <div class="image-options">
              <label>
                <input
                  type="radio"
                  value="none"
                  :checked="image.source === 'none'"
                  @change="updateImageSource(image, 'none')"
                >
                No image
              </label>
              <label>
                <input
                  type="radio"
                  value="url"
                  :checked="image.source === 'url'"
                  @change="updateImageSource(image, 'url')"
                >
                Link to an online image
              </label>
              <label>
                <input
                  type="radio"
                  value="upload"
                  :checked="image.source === 'upload'"
                  @change="updateImageSource(image, 'upload')"
                >
                Upload from your computer
              </label>
            </div>

            <div class="field" v-if="image.source === 'url'">
              <label :for="`image-url-${image.id}`">Image URL</label>
              <input
                :id="`image-url-${image.id}`"
                v-model="image.url"
                type="url"
                placeholder="https://images.unsplash.com/..."
                autocomplete="off"
              >
              <p class="muted helper">Remote URLs are stored directly in the JSON and manifest.</p>
            </div>

            <div class="field" v-else-if="image.source === 'upload'">
              <label :for="`image-file-${image.id}`">Select image</label>
              <input
                :id="`image-file-${image.id}`"
                type="file"
                accept="image/*"
                @change="onImageFileChange($event, image)"
              >
              <p class="muted helper">
                Saved next to the JSON as <code>{{ uploadPathFor(image, index) }}</code>. Recommended size ≥ 1200px wide.
              </p>
              <p v-if="image.fileName" class="file-pill">{{ image.fileName }}</p>
            </div>
          </div>

          <button
            type="button"
            class="btn-secondary add-image-btn"
            @click="addImageEntry"
            :disabled="imageEntries.length >= MAX_IMAGES"
          >
            + Add image
          </button>
        </fieldset>

        <div class="field">
          <label for="video-url">YouTube video (optional)</label>
          <input
            id="video-url"
            v-model="videoUrl"
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            autocomplete="off"
          >
          <p class="muted helper">Paste a YouTube link to embed it after the images. Leave blank to skip.</p>
        </div>

        <div class="actions">
          <button type="submit" class="btn-primary" :disabled="isDrafting">
            <span v-if="isDrafting">Preparing draft…</span>
            <span v-else>Create draft</span>
          </button>
          <button type="button" class="btn-secondary" @click="resetWizard" :disabled="isDrafting">
            Clear form
          </button>
        </div>
      </form>

      <transition name="fade">
        <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>
      </transition>

      <transition name="fade">
        <section v-if="hasDraft" class="review">
          <header>
            <h2>Review &amp; refine</h2>
            <p class="muted helper">Tweak the JSON as needed before saving.</p>
          </header>
          <div class="field">
            <label for="draft-json">Draft JSON</label>
            <textarea id="draft-json" v-model="draftJson" rows="12" spellcheck="false"></textarea>
          </div>

          <p v-if="imageReviewNote" class="muted helper">{{ imageReviewNote }}</p>
          <p v-if="videoReviewNote" class="muted helper">{{ videoReviewNote }}</p>
          <p class="muted helper">{{ saveTargetNote }}</p>

          <div class="field checkbox">
            <label>
              <input type="checkbox" v-model="forceOverwrite">
              Allow overwrite if the JSON file already exists
            </label>
          </div>

          <div v-if="publishEndpointMisconfigured" class="alert error">
            Remote publishing is misconfigured. Ensure <code>VITE_POST_PUBLISH_URL</code> (or
            <code>VITE_CHAT_PUBLISH_URL</code>) points at the publish API endpoint instead of the login URL.
          </div>
          <div v-else-if="remotePublishEnabled" class="alert info">
            Publishing uses the configured API endpoint. The JSON (and optional image) will be committed
            via the serverless workflow after you sign in.
            <p v-if="publishEndpointDerived" class="muted helper">
              Using the publish URL inferred from the login endpoint. Set <code>VITE_POST_PUBLISH_URL</code>
              (or <code>VITE_CHAT_PUBLISH_URL</code>) to override.
            </p>
          </div>
          <div v-else-if="fsSupported" class="connection">
            <p class="muted">
              Repository folder: <strong>{{ repoLabel || 'not connected' }}</strong>
            </p>
            <button class="btn-secondary" type="button" @click="connectRepository">
              {{ repoLabel ? 'Change folder' : 'Connect repository folder' }}
            </button>
            <p class="muted helper">Choose the repo root containing <code>public/content</code>.</p>
          </div>
          <div v-else class="alert info">
            Your browser does not support the File System Access API. Use “Download JSON” and copy
            the file into <code>public/content/{{ contentSubdir }}</code> manually.
          </div>

          <div class="actions">
            <button
              class="btn-secondary"
              type="button"
              :disabled="isSaving || previewLoading || !hasDraft"
              @click="openPreview"
            >
              Preview
            </button>
            <button class="btn-primary" type="button" :disabled="isSaving" @click="publishDraft">
              <span v-if="isSaving">Saving…</span>
              <span v-else>Save to repository</span>
            </button>
          <button class="btn-secondary" type="button" :disabled="isSaving" @click="resetWizard">
            Start over
          </button>
        </div>

          <transition name="fade">
            <div v-if="successMessage" class="alert success">
              {{ successMessage }}
            </div>
          </transition>
        </section>
      </transition>
    </section>

    <transition name="fade">
      <div v-if="isPreviewOpen" class="preview-overlay" @click.self="closePreview">
        <div class="preview-dialog">
          <header class="preview-header">
            <div>
              <p class="muted small">Preview</p>
              <h2 class="preview-title">{{ previewData?.sectionLabel || currentTypeLabel }}</h2>
            </div>
            <button type="button" class="btn-icon close" @click="closePreview" aria-label="Close preview">×</button>
          </header>
          <div class="preview-scroll">
            <div v-if="previewLoading" class="status muted">Loading preview…</div>
            <div v-else-if="previewError" class="alert error">{{ previewError }}</div>
            <template v-else-if="previewData">
              <article class="preview-detail">
                <section class="section gradient-sunrise intro">
                  <div class="container grid2">
                    <div>
                      <div class="eyebrow">{{ previewData.eyebrow }}</div>
                      <h1 class="h2-50">{{ previewData.title }}</h1>
                    </div>
                    <div>
                      <p class="brodtext-20 muted">{{ previewData.intro }}</p>
                      <div v-if="previewData.section === 'events'" class="meta brodtext-20">
                        <strong>{{ previewData.meta }}</strong>
                        <template v-if="previewData.registration">
                          · <a class="more" :href="previewData.registration" target="_blank" rel="noopener">Register »</a>
                        </template>
                      </div>
                      <div v-else-if="previewData.section === 'projects' && previewData.visitUrl" class="visit">
                        <a class="more" :href="previewData.visitUrl" target="_blank" rel="noopener">Visit website »</a>
                      </div>
                    </div>
                  </div>
                  <div v-if="previewData.heroImage" class="container">
                    <div class="hero-img card" :style="{ backgroundImage: `url(${previewData.heroImage})` }"></div>
                  </div>
                </section>

                <section class="section gradient-sunrise body">
                  <div class="container grid2">
                    <div>
                      <h2 class="h3-30">{{ previewData.subheading }}</h2>
                    </div>
                    <div>
                      <p class="brodtext-20 muted" v-for="(paragraph, i) in previewData.bodyParagraphs" :key="i">{{ paragraph }}</p>
                      <div v-if="previewData.gallery.length" class="gallery">
                        <div
                          v-for="(img, i) in previewData.gallery"
                          :key="`${i}-${img}`"
                          class="gallery-card"
                          :style="{ backgroundImage: `url(${img})` }"
                        ></div>
                      </div>
                      <div v-if="previewData.video" class="video-wrap">
                        <iframe
                          :src="previewData.video"
                          title="YouTube video player"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                          referrerpolicy="strict-origin-when-cross-origin"
                          allowfullscreen
                        ></iframe>
                      </div>
                    </div>
                  </div>
                </section>

                <section v-if="previewData.contacts.length" class="section contacts">
                  <div class="container">
                    <h3 class="h3-30">Contacts</h3>
                    <div class="people">
                      <div class="person" v-for="contact in previewData.contacts" :key="contact.id">
                        <div v-if="contact.image" class="avatar" :style="{ backgroundImage: `url(${contact.image})` }"></div>
                        <div class="name">{{ contact.name }}</div>
                        <div v-if="contact.title" class="role muted">{{ contact.title }}</div>
                        <a v-if="contact.email" class="more" :href="`mailto:${contact.email}`">Email »</a>
                      </div>
                    </div>
                  </div>
                </section>

                <section v-if="previewData.related.length" class="section gradient-sunrise related">
                  <div class="container">
                    <h3 class="h3-30 section-title">Related {{ previewData.section === 'projects' ? 'projects' : 'posts' }}</h3>
                    <div class="cards">
                      <article v-for="related in previewData.related" :key="related.id" class="card project">
                        <div class="img" :style="{ backgroundImage: related.image ? `url(${related.image})` : undefined }"></div>
                        <div class="body">
                          <h4 class="h3-30">{{ related.title }}</h4>
                          <p class="brodtext-20 muted">{{ related.summary }}</p>
                          <span class="more">{{ previewData.section === 'projects' ? 'Read more »' : 'Read more »' }}</span>
                        </div>
                      </article>
                    </div>
                  </div>
                </section>
              </article>
            </template>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { resolvePostEndpoints } from '../utils/postEndpoints'
import { ensureYouTubeEmbed, toYouTubeEmbed } from '../utils/video'
import { sanitizeSrc, sanitizeUrl } from '../utils/sanitize'
import { resolveUrl, withBase } from '../utils/paths.js'

const TYPE_OPTIONS = [
  { value: 'news', label: 'News' },
  { value: 'events', label: 'Events' },
  { value: 'projects', label: 'Projects' },
]

const SECTION_CONFIG = {
  news: { label: 'News', contentDir: 'news', urlPrefix: '/news/' },
  events: { label: 'Events', contentDir: 'events', urlPrefix: '/events/' },
  projects: { label: 'Projects', contentDir: 'projects', urlPrefix: '/projects/' },
}

const {
  publishEndpoint: resolvedPublishEndpoint,
  publishDerivedFromAuth,
  publishMisconfigured,
} = resolvePostEndpoints()
const publishEndpoint = resolvedPublishEndpoint
const publishEndpointDerived = publishDerivedFromAuth
const publishEndpointMisconfigured = publishMisconfigured
const remotePublishEnabled = computed(() => Boolean(publishEndpoint))
const authSession = inject('postAuthSession', ref({ token: '', expiresAt: 0 }))
const authToken = inject('postAuthToken', ref(''))
const basePath = (import.meta.env.BASE_URL || '/').replace(/\/$/, '')

const typeOptions = TYPE_OPTIONS

const postType = ref('news')
const title = ref('')
const bodyInput = ref('')
const slug = ref('')
const slugWasEdited = ref(false)
const selectedDate = ref(new Date().toISOString().slice(0, 10))
const MAX_RELATED = 4
const MAX_CONTACTS = 2
const relatedOptions = ref([])
const relatedLoading = ref(false)
const relatedError = ref('')
const selectedRelated = ref([])
const relatedSelectionFull = computed(() => selectedRelated.value.length >= MAX_RELATED)
const contactOptions = ref([])
const contactLoading = ref(false)
const contactError = ref('')
const selectedContacts = ref([])
const contactSelectionFull = computed(() => selectedContacts.value.length >= MAX_CONTACTS)

const MAX_IMAGES = 6
const imageEntries = ref([])
const preparedImages = ref([])
initializeImageEntries()
const videoUrl = ref('')
const preparedVideo = ref('')

const draftSection = ref(null)
const draftJson = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const forceOverwrite = ref(false)
const isDrafting = ref(false)
const isSaving = ref(false)
const repoLabel = ref('')
const rootHandle = ref(null)
const isPreviewOpen = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const previewData = ref(null)
const previewObjectUrls = ref([])

const fsSupported = typeof window !== 'undefined' && 'showDirectoryPicker' in window

const sectionConfig = computed(() => SECTION_CONFIG[postType.value] || SECTION_CONFIG.news)
const contentSubdir = computed(() => sectionConfig.value.contentDir)
const currentTypeLabel = computed(() => sectionConfig.value.label)
const draftSectionLabel = computed(() =>
  draftSection.value ? (SECTION_CONFIG[draftSection.value]?.label || draftSection.value) : ''
)

const computedSlug = computed(() => slug.value.trim() || slugify(title.value))
const hasDraft = computed(() => Boolean(draftJson.value.trim()))

const hasUploadImages = computed(() =>
  preparedImages.value.some((img) => img.type === 'upload' && img.file)
)

const imageReviewNote = computed(() => {
  if (!hasDraft.value) return ''
  if (!preparedImages.value.length) {
    return 'No images selected. Manifest entry will omit an image reference.'
  }
  const [headline, ...extras] = preparedImages.value
  const parts = []
  if (headline) {
    const detail =
      headline.type === 'upload'
        ? `will be saved as ${headline.jsonValue}`
        : `uses ${headline.jsonValue}`
    parts.push(`Headline image ${detail}.`)
  }
  if (extras.length) {
    const uploadCount = extras.filter((img) => img.type === 'upload').length
    const remoteCount = extras.length - uploadCount
    const detailSegments = []
    if (uploadCount) detailSegments.push(`${uploadCount} upload${uploadCount > 1 ? 's' : ''}`)
    if (remoteCount) detailSegments.push(`${remoteCount} remote URL${remoteCount > 1 ? 's' : ''}`)
    parts.push(`Additional images include ${detailSegments.join(' and ')}.`)
  }
  return parts.join(' ')
})

const videoReviewNote = computed(() => {
  if (!hasDraft.value) return ''
  if (preparedVideo.value) {
    return `Embedding YouTube video ${preparedVideo.value}.`
  }
  const parsed = tryParseDraft()
  if (parsed?.video) {
    return `Draft references video ${parsed.video}.`
  }
  if (videoUrl.value.trim()) {
    return 'Video link could not be parsed as a YouTube URL.'
  }
  return ''
})

const saveTargetNote = computed(() => {
  const dir = contentSubdir.value
  if (draftSection.value && draftSection.value !== postType.value) {
    return `Saving will write into public/content/${dir}/ (current selection: ${currentTypeLabel.value}). Regenerate the draft to align fields after switching from ${draftSectionLabel.value || 'another type'}.`
  }
  return `Saving will write into public/content/${dir}/.`
})

watch(title, (value) => {
  if (!slugWasEdited.value) {
    slug.value = slugify(value)
  }
})

watch(slug, (value) => {
  if (!value) {
    slugWasEdited.value = false
  }
})

watch(postType, (section) => {
  selectedRelated.value = []
  refreshRelatedOptions(section)
  selectedContacts.value = []
  if (section === 'events') {
    contactOptions.value = []
    contactError.value = ''
    contactLoading.value = false
  } else {
    ensureContactsLoaded()
  }
})

onMounted(() => {
  refreshRelatedOptions(postType.value)
  if (postType.value !== 'events') {
    ensureContactsLoaded()
  }
})

function slugify(value = '') {
  return value
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || 'post-entry'
}

function inferExtensionFromName(name = '') {
  const match = name.toLowerCase().match(/\.(jpg|jpeg|png|webp|gif|avif)$/)
  return match ? match[0] : ''
}

function deriveExtension(file) {
  if (!file) return ''
  const fromName = inferExtensionFromName(file.name || '')
  if (fromName) return fromName
  const map = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
    'image/avif': '.avif',
  }
  return map[file.type] || ''
}

function uploadPathFor(entry, index) {
  const baseSlug = computedSlug.value || 'post-entry'
  const displayIndex = displayIndexFor(index)
  const suffix = displayIndex === 0 ? '' : `-${displayIndex}`
  const ext = entry.fileExtension || inferExtensionFromName(entry.fileName) || '.jpg'
  return `content/${contentSubdir.value}/${baseSlug}${suffix}${ext}`
}

function displayIndexFor(index) {
  let count = 0
  for (let i = 0; i < index; i += 1) {
    const entry = imageEntries.value[i]
    if (!entry) continue
    if (entry.source === 'upload') {
      count += 1
      continue
    }
    if (entry.source === 'url' && entry.url && entry.url.trim()) {
      count += 1
    }
  }
  return count
}

function updateImageSource(entry, mode) {
  entry.source = mode
  if (mode !== 'upload') {
    entry.file = null
    entry.fileName = ''
    entry.fileExtension = ''
  }
  if (mode !== 'url') {
    entry.url = ''
  }
}

function onImageFileChange(event, entry) {
  const file = event?.target?.files?.[0]
  if (!file) {
    entry.file = null
    entry.fileName = ''
    entry.fileExtension = ''
    return
  }
  entry.file = file
  entry.fileName = file.name || 'uploaded-image'
  entry.fileExtension = deriveExtension(file)
}

function addImageEntry() {
  if (imageEntries.value.length >= MAX_IMAGES) return
  imageEntries.value = [...imageEntries.value, createImageEntry()]
}

function removeImageEntry(index) {
  if (index <= 0) return
  const next = [...imageEntries.value]
  next.splice(index, 1)
  imageEntries.value = next.length ? next : [createImageEntry({ isHero: true })]
}

function initializeImageEntries() {
  imageEntries.value = [createImageEntry({ isHero: true })]
}

function createImageEntry({ isHero = false } = {}) {
  return {
    id: `img-${Math.random().toString(36).slice(2, 10)}`,
    isHero,
    source: isHero ? 'none' : 'upload',
    url: '',
    file: null,
    fileName: '',
    fileExtension: '',
  }
}

function resolveImageEntry(entry, { displayIndex, slugValue, contentDir }) {
  if (!entry) return null
  if (entry.source === 'none') return null
  if (entry.source === 'url') {
    const remote = (entry.url || '').trim()
    if (!remote) return null
    return {
      type: 'url',
      image: remote,
      ext: '',
      file: null,
    }
  }
  if (entry.source === 'upload') {
    const file = entry.file
    if (!file) {
      const label = displayIndex === 0 ? 'headline image' : `image #${displayIndex + 1}`
      throw new Error(`Select a file for the ${label} or remove it.`)
    }
    const ext = entry.fileExtension || deriveExtension(file) || '.jpg'
    const suffix = displayIndex === 0 ? '' : `-${displayIndex}`
    const filename = `${slugValue}${suffix}${ext}`
    const jsonValue = `content/${contentDir}/${filename}`
    return {
      type: 'upload',
      image: jsonValue,
      ext,
      file,
    }
  }
  return null
}

async function refreshRelatedOptions(section) {
  if (section === 'events') {
    relatedOptions.value = []
    relatedError.value = ''
    relatedLoading.value = false
    selectedRelated.value = []
    return
  }

  const config = SECTION_CONFIG[section]
  if (!config) {
    relatedOptions.value = []
    relatedError.value = ''
    relatedLoading.value = false
    return
  }

  relatedLoading.value = true
  relatedError.value = ''
  try {
    const manifestUrl = `${basePath}/content/${config.contentDir}/index.json`
    const res = await fetch(manifestUrl, { cache: 'no-store' })
    const manifest = res.ok ? await res.json() : null
    const items = Array.isArray(manifest?.items)
      ? manifest.items
      : Array.isArray(manifest) ? manifest : []

    const options = []
    for (const entry of items) {
      const slugValue = typeof entry === 'string'
        ? entry
        : entry?.base || entry?.id || entry?.slug || entry?.name
      if (!slugValue) continue

      try {
        const detailUrl = `${basePath}/content/${config.contentDir}/${slugValue}.json`
        const detailRes = await fetch(detailUrl, { cache: 'no-store' })
        if (!detailRes.ok) continue
        const detail = await detailRes.json()
        const titleValue = detail?.title || detail?.name || slugValue
        options.push({ slug: slugValue, title: titleValue })
      } catch (_) {
        // ignore individual fetch failures
      }
    }

    relatedOptions.value = options
    selectedRelated.value = selectedRelated.value.filter((slug) =>
      options.some((option) => option.slug === slug)
    )
  } catch (err) {
    relatedError.value = err instanceof Error ? err.message : String(err)
    relatedOptions.value = []
    relatedRecord.value = {}
  } finally {
    relatedLoading.value = false
  }
}

function isRelatedSelected(slugValue) {
  return selectedRelated.value.includes(slugValue)
}

function toggleRelated(slugValue, checked) {
  if (checked) {
    if (isRelatedSelected(slugValue) || selectedRelated.value.length >= MAX_RELATED) return
    selectedRelated.value = [...selectedRelated.value, slugValue]
  } else {
    selectedRelated.value = selectedRelated.value.filter((item) => item !== slugValue)
  }
}

let contactsLoaded = false
async function ensureContactsLoaded() {
  if (contactsLoaded) return
  await refreshContactOptions()
  contactsLoaded = true
}

async function refreshContactOptions() {
  contactLoading.value = true
  contactError.value = ''
  try {
    const res = await fetch(`${basePath}/content/users.json`, { cache: 'no-store' })
    if (!res.ok) {
      throw new Error(`Contacts request failed (${res.status})`)
    }
    const payload = await res.json()
    const items = Array.isArray(payload?.users)
      ? payload.users
      : Array.isArray(payload) ? payload : []

    const options = []
    for (const entry of items) {
      if (!entry) continue
      const slugValue = entry.slug || entry.id || entry.username || entry.email
      if (!slugValue) continue
      options.push({
        slug: slugValue,
        name: entry.name || entry.displayName || slugValue,
        email: entry.email || '',
        title: entry.title || entry.role || '',
      })
    }
    contactOptions.value = options
    selectedContacts.value = selectedContacts.value.filter((slug) =>
      options.some((option) => option.slug === slug)
    )
    contactsLoaded = true
  } catch (err) {
    contactError.value = err instanceof Error ? err.message : String(err)
    contactOptions.value = []
    selectedContacts.value = []
    contactsLoaded = false
  } finally {
    contactLoading.value = false
  }
}

function isContactSelected(slugValue) {
  return selectedContacts.value.includes(slugValue)
}

function toggleContact(slugValue, checked) {
  if (checked) {
    if (isContactSelected(slugValue) || selectedContacts.value.length >= MAX_CONTACTS) return
    selectedContacts.value = [...selectedContacts.value, slugValue]
  } else {
    selectedContacts.value = selectedContacts.value.filter((item) => item !== slugValue)
  }
}

function createSummary(body) {
  if (!body) return ''
  const paragraph = body.split(/\n{2,}/)[0] || ''
  const condensed = paragraph.replace(/\s+/g, ' ').trim()
  if (!condensed) return ''
  if (condensed.length <= 180) return condensed
  return `${condensed.slice(0, 177).trimEnd()}…`
}

function prepareDraft() {
  errorMessage.value = ''
  successMessage.value = ''

  const titleValue = title.value.trim()
  const bodyValue = bodyInput.value.replace(/\r\n/g, '\n').trim()

  if (!titleValue || !bodyValue) {
    errorMessage.value = 'Provide a title and body before creating a draft.'
    return
  }

  isDrafting.value = true
  try {
    const slugValue = computedSlug.value || 'post-entry'
    slug.value = slugValue
    slugWasEdited.value = true

    const normalizedBody = bodyValue
      .split('\n')
      .map((line) => line.replace(/\s+$/g, ''))
      .join('\n')
      .trim()
    const summary = createSummary(normalizedBody)
  const isoDate = selectedDate.value || new Date().toISOString().slice(0, 10)
    const section = postType.value
    const config = SECTION_CONFIG[section] || SECTION_CONFIG.news
    const contentDir = config.contentDir

    const collectedImages = []
    const preparedList = []
    imageEntries.value.forEach((entry, index) => {
      if (!entry) return
      const resolved = resolveImageEntry(entry, {
        displayIndex: collectedImages.length,
        slugValue,
        contentDir,
      })
      if (!resolved) return
      collectedImages.push(resolved.image)
      preparedList.push({
        type: resolved.type,
        jsonValue: resolved.image,
        ext: resolved.ext || '',
        file: resolved.file || null,
        section,
        entryIndex: index,
        displayIndex: collectedImages.length - 1,
      })
    })
    preparedImages.value = preparedList

    let videoEntry = ''
    if (videoUrl.value.trim()) {
      videoEntry = toYouTubeEmbed(videoUrl.value)
      if (!videoEntry) {
        preparedVideo.value = ''
        throw new Error('Provide a valid YouTube link or leave the video field blank.')
      }
      preparedVideo.value = videoEntry
    } else {
      preparedVideo.value = ''
    }

    let payload
    if (section === 'events') {
      payload = {
        title: titleValue,
        summary,
        body: normalizedBody,
        date: isoDate,
      }
    } else if (section === 'projects') {
      payload = {
        title: titleValue,
        intro: summary,
        description: summary,
        summary,
        body: normalizedBody,
        subheading: 'Details',
        url: `${config.urlPrefix}${slugValue}`,
        date: isoDate,
      }
    } else {
      payload = {
        title: titleValue,
        summary,
        url: `${config.urlPrefix}${slugValue}`,
        body: normalizedBody,
        eyebrow: 'News',
        date: isoDate,
      }
    }

    if (collectedImages.length) {
      payload.image = collectedImages[0]
      payload.images = collectedImages
    } else {
      delete payload.image
      delete payload.images
    }

    if (videoEntry) {
      payload.video = videoEntry
    } else {
      delete payload.video
    }

  if (postType.value !== 'events') {
    if (selectedRelated.value.length) {
      payload.related = [...selectedRelated.value]
    } else {
      delete payload.related
    }
    if (selectedContacts.value.length) {
      payload.contacts = [...selectedContacts.value]
    } else {
      delete payload.contacts
    }
  }

    draftSection.value = section
    draftJson.value = JSON.stringify(payload, null, 2)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
  } finally {
    isDrafting.value = false
  }
}

async function connectRepository() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!fsSupported) {
    errorMessage.value = 'File System Access API is not available in this browser.'
    return
  }

  try {
    const handle = await window.showDirectoryPicker({ id: 'dtcc-web-root' })
    if (handle.requestPermission) {
      const permission = await handle.requestPermission({ mode: 'readwrite' })
      if (permission === 'denied') {
        throw new Error('Permission denied for the selected directory.')
      }
    }
    rootHandle.value = handle
    repoLabel.value = handle.name
  } catch (err) {
    if (err?.name === 'AbortError') return
    errorMessage.value = err instanceof Error ? err.message : String(err)
  }
}

async function ensureRepoHandle() {
  if (!fsSupported) {
    throw new Error('File System Access API is not available in this browser.')
  }
  if (!rootHandle.value) {
    await connectRepository()
  }
  if (!rootHandle.value) {
    throw new Error('Select your repository folder before saving.')
  }
  if (rootHandle.value.requestPermission) {
    const status = await rootHandle.value.queryPermission?.({ mode: 'readwrite' })
    if (status === 'denied') {
      throw new Error('Permission denied for the selected directory.')
    }
    if (status !== 'granted') {
      const permission = await rootHandle.value.requestPermission({ mode: 'readwrite' })
      if (permission !== 'granted') {
        throw new Error('Permission denied for the selected directory.')
      }
    }
  }
  repoLabel.value = rootHandle.value.name
  return rootHandle.value
}

async function getContentDirectory(root, dirName) {
  try {
    const publicDir = await root.getDirectoryHandle('public')
    const contentDir = await publicDir.getDirectoryHandle('content')
    return await contentDir.getDirectoryHandle(dirName)
  } catch (err) {
    throw new Error(`Selected folder must contain public/content/${dirName}/.`)
  }
}

async function writeJsonFile(dirHandle, filename, data, { force }) {
  const pretty = `${JSON.stringify(data, null, 2)}\n`

  try {
    const existingHandle = await dirHandle.getFileHandle(filename)
    if (!force) {
      throw new Error(`${filename} already exists. Enable overwrite to replace it.`)
    }
    const writable = await existingHandle.createWritable()
    await writable.write(pretty)
    await writable.close()
    return existingHandle
  } catch (err) {
    if (err?.name === 'NotFoundError') {
      const handle = await dirHandle.getFileHandle(filename, { create: true })
      const writable = await handle.createWritable()
      await writable.write(pretty)
      await writable.close()
      return handle
    }
    throw err
  }
}

async function writeBinaryFile(dirHandle, filename, file, { force }) {
  try {
    const existingHandle = await dirHandle.getFileHandle(filename)
    if (!force) {
      throw new Error(`${filename} already exists. Enable overwrite to replace it.`)
    }
    const writable = await existingHandle.createWritable()
    await writable.write(await file.arrayBuffer())
    await writable.close()
    return existingHandle
  } catch (err) {
    if (err?.name === 'NotFoundError') {
      const handle = await dirHandle.getFileHandle(filename, { create: true })
      const writable = await handle.createWritable()
      await writable.write(await file.arrayBuffer())
      await writable.close()
      return handle
    }
    throw err
  }
}

async function updateManifest(sectionDir, section, slugValue, data, image, { force }) {
  let handle
  try {
    handle = await sectionDir.getFileHandle('index.json')
  } catch (err) {
    if (err?.name === 'NotFoundError') {
      handle = await sectionDir.getFileHandle('index.json', { create: true })
    } else {
      throw err
    }
  }

  let manifest = { items: [] }
  try {
    const file = await handle.getFile()
    const text = await file.text()
    if (text.trim()) {
      manifest = JSON.parse(text)
    }
  } catch (err) {
    throw new Error('Unable to parse index.json. Fix the file manually before continuing.')
  }

  if (!Array.isArray(manifest.items)) {
    throw new Error('index.json must contain an array under "items".')
  }

  let added = false

  if (section === 'news' || section === 'projects') {
    const entry = image ? { base: slugValue, image } : { base: slugValue }
    const index = manifest.items.findIndex((item) => {
      if (typeof item === 'string') return item === slugValue
      return item && typeof item === 'object' && (item.base === slugValue || item.id === slugValue)
    })

    if (index === -1) {
      manifest.items.push(entry)
      added = true
    } else if (force) {
      const prev = manifest.items[index]
      if (typeof prev === 'string') {
        manifest.items[index] = entry
      } else if (prev && typeof prev === 'object') {
        const next = { ...prev }
        if (image) {
          next.image = image
        }
        manifest.items[index] = next
      } else {
        manifest.items[index] = entry
      }
    }
  } else if (section === 'events') {
    const entry = {
      id: slugValue,
      title: data.title || slugValue,
    }
    if (data.date) entry.date = data.date
    if (data.timeStart) entry.timeStart = data.timeStart
    if (data.timeEnd) entry.timeEnd = data.timeEnd
    if (data.location) entry.location = data.location
    if (data.meta) entry.meta = data.meta

    const index = manifest.items.findIndex((item) => {
      if (!item) return false
      if (typeof item === 'string') return item === slugValue
      if (typeof item === 'object') {
        const key = item.id || item.slug || item.base
        return key === slugValue
      }
      return false
    })

    if (index === -1) {
      manifest.items.push(entry)
      added = true
    } else if (force) {
      const prev = manifest.items[index]
      if (prev && typeof prev === 'object') {
        manifest.items[index] = { ...prev, ...entry }
      } else {
        manifest.items[index] = entry
      }
    }
  }

  const writer = await handle.createWritable()
  await writer.write(`${JSON.stringify(manifest, null, 2)}\n`)
  await writer.close()

  return added
}

async function publishDraft() {
  if (!hasDraft.value) return

  errorMessage.value = ''
  successMessage.value = ''

  let parsed
  try {
    parsed = JSON.parse(draftJson.value)
  } catch (err) {
    errorMessage.value = 'Fix the JSON before saving.'
    return
  }

  if (!parsed.title) {
    errorMessage.value = 'The JSON needs a "title" field before publishing.'
    return
  }

  if (postType.value !== 'events') {
    if (selectedRelated.value.length) {
      parsed.related = [...selectedRelated.value]
    } else {
      delete parsed.related
    }
    if (selectedContacts.value.length) {
      parsed.contacts = [...selectedContacts.value]
    } else {
      delete parsed.contacts
    }
  } else {
    delete parsed.related
    delete parsed.contacts
  }

  const slugValue = slug.value.trim() || slugify(parsed.title)
  slug.value = slugValue
  slugWasEdited.value = true

  const section = postType.value
  const config = SECTION_CONFIG[section] || SECTION_CONFIG.news

  if (typeof parsed.video === 'string') {
    const normalizedVideo = ensureYouTubeEmbed(parsed.video)
    if (parsed.video.trim() && !normalizedVideo) {
      errorMessage.value = 'Video must be a valid YouTube link or embed.'
      return
    }
    if (normalizedVideo) {
      parsed.video = normalizedVideo
    } else {
      delete parsed.video
    }
  } else if (parsed.video != null) {
    delete parsed.video
  }

  const uploadStates = preparedImages.value.filter((img) => img.type === 'upload' && img.file)

  if (uploadStates.length) {
    const expectedPrefix = `content/${config.contentDir}/`
    const imagesArray = Array.isArray(parsed.images) ? [...parsed.images] : []
    uploadStates.forEach((state) => {
      const ext = state.ext || (state.file ? deriveExtension(state.file) : '') || '.jpg'
      const suffix = state.displayIndex === 0 ? '' : `-${state.displayIndex}`
      const filename = `${slugValue}${suffix}${ext}`
      const imagePath = `${expectedPrefix}${filename}`
      imagesArray[state.displayIndex] = imagePath
      if (state.displayIndex === 0) {
        parsed.image = imagePath
      }
      state.jsonValue = imagePath
      state.section = section
      state.ext = ext
    })
    parsed.images = imagesArray
  }

  if (Array.isArray(parsed.images) && parsed.images.length && !parsed.image) {
    parsed.image = parsed.images[0]
  }

  const manifestImage = section === 'events' ? '' : (typeof parsed.image === 'string' ? parsed.image.trim() : '')
  const commitMessage = buildCommitMessage(section, slugValue)

  isSaving.value = true
  try {
    if (remotePublishEnabled.value) {
      await publishViaApi({ parsed, slugValue, section, uploadStates, config, commitMessage })
    } else {
      await publishToFileSystem({ parsed, slugValue, section, uploadStates, config, manifestImage })
    }
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
  } finally {
    isSaving.value = false
  }
}

function buildCommitMessage(section, slugValue) {
  const label = SECTION_CONFIG[section]?.label || section.charAt(0).toUpperCase() + section.slice(1)
  return `Add ${label} entry ${slugValue}`
}

async function publishToFileSystem({ parsed, slugValue, section, uploadStates, config, manifestImage }) {
  const root = await ensureRepoHandle()
  const sectionDir = await getContentDirectory(root, config.contentDir)

  await writeJsonFile(sectionDir, `${slugValue}.json`, parsed, { force: forceOverwrite.value })

  if (uploadStates && uploadStates.length) {
    const expectedPrefix = `content/${config.contentDir}/`
    for (const state of uploadStates) {
      if (!state.file) continue
      const imagePath = typeof state.jsonValue === 'string' ? state.jsonValue : ''
      if (!imagePath.startsWith(expectedPrefix)) {
        throw new Error(`Uploaded image path must live under ${expectedPrefix}. Update the JSON before saving.`)
      }
      const targetName = imagePath.slice(expectedPrefix.length)
      await writeBinaryFile(sectionDir, targetName, state.file, { force: forceOverwrite.value })
    }
  }

  const added = await updateManifest(sectionDir, section, slugValue, parsed, manifestImage, { force: forceOverwrite.value })

  successMessage.value = `Saved public/content/${config.contentDir}/${slugValue}.json${added ? ' and updated index.json.' : '.'}`
  draftSection.value = section
}

async function publishViaApi({ parsed, slugValue, section, uploadStates, config, commitMessage }) {
  if (!publishEndpoint) {
    throw new Error('Publish endpoint is not configured.')
  }
  const token = getSessionToken()
  if (!token) {
    throw new Error('Your login session has expired. Please sign in again.')
  }

  const body = {
    section,
    slug: slugValue,
    payload: parsed,
    force: forceOverwrite.value,
  }
  if (commitMessage) {
    body.commitMessage = commitMessage
  }

  if (uploadStates && uploadStates.length) {
    const expectedPrefix = `content/${config.contentDir}/`
    body.imageUploads = []
    for (const state of uploadStates) {
      if (!state.file) continue
      const imagePath = typeof state.jsonValue === 'string'
        ? state.jsonValue
        : (Array.isArray(parsed.images) ? parsed.images[state.displayIndex] : '')
      if (!imagePath || !imagePath.startsWith(expectedPrefix)) {
        throw new Error(`Uploaded image path must live under ${expectedPrefix}. Update the JSON before saving.`)
      }
      const filename = imagePath.slice(expectedPrefix.length)
      body.imageUploads.push({
        filename,
        index: state.displayIndex,
        contentType: state.file.type || 'application/octet-stream',
        data: await fileToBase64(state.file),
      })
    }
    if (!body.imageUploads.length) {
      delete body.imageUploads
    }
  }

  let response
  try {
    response = await fetch(publishEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    })
  } catch (err) {
    throw new Error(err instanceof Error ? err.message : 'Network error while publishing.')
  }

  let payload = {}
  try {
    payload = await response.json()
  } catch (_) {
    payload = {}
  }

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error(payload?.error || 'Session expired. Please sign in again.')
    }
    const message = typeof payload?.error === 'string'
      ? payload.error
      : `Publish failed (status ${response.status})`
    throw new Error(message)
  }

  const manifestUpdated = Boolean(payload?.manifestUpdated)
  const manifestNote = manifestUpdated ? ' (manifest updated).' : '.'
  successMessage.value = `Published ${config.contentDir}/${slugValue}.json via API${manifestNote} Updates will be live within ~30 seconds.`
  draftSection.value = section
}

async function fileToBase64(file) {
  const buffer = await file.arrayBuffer()
  const bytes = new Uint8Array(buffer)
  const chunkSize = 0x8000
  let binary = ''
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = bytes.subarray(i, i + chunkSize)
    binary += String.fromCharCode(...chunk)
  }
  return btoa(binary)
}

function getSessionToken() {
  if (authSession) {
    const sessionData = typeof authSession === 'object' && 'value' in authSession
      ? authSession.value
      : authSession
    if (sessionData && sessionData.token) {
      const expiresAt = Number(sessionData.expiresAt) || 0
      if (!expiresAt || expiresAt * 1000 > Date.now()) {
        return sessionData.token
      }
      return ''
    }
  }
  if (!authToken) return ''
  if (typeof authToken === 'string') return authToken
  return authToken.value || ''
}

function downloadDraft() {
  if (!hasDraft.value) return

  const slugValue = computedSlug.value || 'post-entry'
  const blob = new Blob([draftJson.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${slugValue}.json`
  anchor.click()
  URL.revokeObjectURL(url)

  const uploads = preparedImages.value.filter((img) => img.type === 'upload' && img.file)
  if (!uploads.length) return
  const expectedPrefix = `content/${contentSubdir.value}/`
  uploads.forEach((state) => {
    if (!state.file) return
    let filename = typeof state.jsonValue === 'string' ? state.jsonValue : ''
    if (filename && filename.startsWith(expectedPrefix)) {
      filename = filename.slice(expectedPrefix.length)
    } else {
      const suffix = state.displayIndex === 0 ? '' : `-${state.displayIndex}`
      const ext = state.ext || deriveExtension(state.file) || '.jpg'
      filename = `${slugValue}${suffix}${ext}`
    }
    const imageUrl = URL.createObjectURL(state.file)
    const imageAnchor = document.createElement('a')
    imageAnchor.href = imageUrl
    imageAnchor.download = filename
    imageAnchor.click()
    URL.revokeObjectURL(imageUrl)
  })
}

function resetWizard() {
  title.value = ''
  bodyInput.value = ''
  slug.value = ''
  slugWasEdited.value = false
  selectedDate.value = new Date().toISOString().slice(0, 10)
  initializeImageEntries()
  preparedImages.value = []
  videoUrl.value = ''
  preparedVideo.value = ''
  draftSection.value = null
  draftJson.value = ''
  successMessage.value = ''
  errorMessage.value = ''
  forceOverwrite.value = false
  selectedRelated.value = []
  selectedContacts.value = []
}

function tryParseDraft() {
  if (!draftJson.value.trim()) return null
  try {
    return JSON.parse(draftJson.value)
  } catch (_) {
    return null
  }
}

async function openPreview() {
  if (!hasDraft.value) {
    errorMessage.value = 'Create a draft before opening the preview.'
    return
  }

  previewError.value = ''
  previewLoading.value = true
  isPreviewOpen.value = true
  cleanupPreviewResources()

  let parsed
  try {
    parsed = JSON.parse(draftJson.value)
  } catch (_) {
    previewLoading.value = false
    previewError.value = 'Fix the JSON before previewing.'
    previewData.value = null
    return
  }

  const section = (draftSection.value || postType.value || 'news')
  try {
    const images = collectPreviewImages(parsed)
    const heroImage = images[0] || ''
    const galleryImages = images.slice(1)
    const video = preparedVideo.value || ensureYouTubeEmbed(parsed.video || '') || ''
    const bodyParagraphs = splitBodyParagraphs(parsed.body)
    const sectionLabel = SECTION_CONFIG[section]?.label || section
    const eyebrow = section === 'news' ? 'News:' : section === 'projects' ? 'Project:' : 'Event:'

    let meta = ''
    let registration = ''
    let visitUrl = ''
    if (section === 'events') {
      meta = parsed.meta || formatEventMeta(parsed)
      registration = normalizePreviewLink(parsed.registration || '')
    } else if (section === 'projects') {
      visitUrl = normalizePreviewLink(parsed.url || '')
    }

    const related = section === 'events'
      ? []
      : await loadPreviewRelated(section, Array.isArray(parsed.related) ? parsed.related : [])

    const contacts = section === 'events'
      ? []
      : await loadPreviewContacts(Array.isArray(parsed.contacts) ? parsed.contacts : [])

    previewData.value = {
      section,
      sectionLabel,
      eyebrow,
      title: parsed.title || 'Untitled entry',
      intro: parsed.intro || parsed.summary || '',
      subheading: parsed.subheading || parsed.headline || 'Details',
      bodyParagraphs,
      heroImage,
      gallery: galleryImages,
      video,
      meta,
      registration,
      visitUrl,
      related,
      contacts,
    }
    previewError.value = ''
  } catch (err) {
    previewError.value = err instanceof Error ? err.message : String(err)
    previewData.value = null
  } finally {
    previewLoading.value = false
  }
}

function closePreview() {
  cleanupPreviewResources()
  isPreviewOpen.value = false
  previewLoading.value = false
  previewError.value = ''
  previewData.value = null
}

function cleanupPreviewResources() {
  previewObjectUrls.value.forEach((url) => {
    try {
      URL.revokeObjectURL(url)
    } catch (_) {
      /* ignore */
    }
  })
  previewObjectUrls.value = []
}

function createPreviewObjectUrl(file) {
  const url = URL.createObjectURL(file)
  previewObjectUrls.value.push(url)
  return url
}

function collectPreviewImages(parsed) {
  const urls = []
  const add = (value) => {
    if (!value) return
    if (!urls.includes(value)) urls.push(value)
  }

  if (preparedImages.value.length) {
    preparedImages.value.forEach((entry) => {
      if (entry.type === 'upload' && entry.file) {
        add(createPreviewObjectUrl(entry.file))
      } else {
        add(sanitizePreviewImage(entry.jsonValue))
      }
    })
  }

  if (!urls.length) {
    const candidates = []
    if (typeof parsed.image === 'string') candidates.push(parsed.image)
    if (Array.isArray(parsed.images)) candidates.push(...parsed.images)
    candidates.forEach((candidate) => add(sanitizePreviewImage(candidate)))
  }

  return urls
}

function sanitizePreviewImage(value) {
  if (!value || typeof value !== 'string') return ''
  if (value.startsWith('blob:') || value.startsWith('data:')) return value
  try {
    const resolved = resolveUrl(value)
    if (!resolved || typeof resolved !== 'string') return ''
    return sanitizeSrc(resolved)
  } catch (_) {
    return ''
  }
}

function splitBodyParagraphs(value) {
  if (!value) return []
  if (Array.isArray(value)) return value
  return String(value).split(/\n\n+/).map((s) => s.trim()).filter(Boolean)
}

function normalizePreviewLink(value) {
  if (!value) return ''
  const trimmed = String(value).trim()
  if (!trimmed) return ''
  if (trimmed.startsWith('/')) {
    return withBase(trimmed.replace(/^\/+/, ''))
  }
  if (/^[a-z][a-z\d+\-.]*:/.test(trimmed)) {
    return sanitizeUrl(trimmed)
  }
  try {
    const resolved = resolveUrl(trimmed)
    if (!resolved || typeof resolved !== 'string') return ''
    if (/^[a-z][a-z\d+\-.]*:/.test(resolved)) {
      return sanitizeUrl(resolved)
    }
    if (resolved.startsWith('/')) {
      return withBase(resolved.replace(/^\/+/, ''))
    }
    return sanitizeUrl(resolved)
  } catch (_) {
    return ''
  }
}

function formatEventMeta(detail) {
  const fallback = [detail.location || ''].filter(Boolean).join(', ')
  if (!detail?.date) return fallback
  const dateObj = new Date(detail.date)
  if (Number.isNaN(dateObj.getTime())) return fallback
  const month = dateObj.toLocaleString(undefined, { month: 'long' })
  const day = dateObj.getDate()
  const suffix = ['th', 'st', 'nd', 'rd']
  const mod = day % 100
  const daySuffix = suffix[(mod - 20) % 10] || suffix[mod] || suffix[0]
  const start = detail.timeStart || ''
  const end = detail.timeEnd || ''
  const time = start && end ? `${start}–${end}` : start || end || ''
  return [ `${month} ${day}${daySuffix}`, time, detail.location || '' ].filter(Boolean).join(', ')
}

async function loadPreviewRelated(section, slugs) {
  const targetSection = section === 'projects' ? 'projects' : 'news'
  const result = []
  if (!Array.isArray(slugs) || !slugs.length) return result
  const limited = slugs.slice(0, 3)
  for (const slug of limited) {
    const data = await fetchContentEntry(targetSection, slug)
    if (!data) continue
    result.push({
      id: slug,
      title: data.title || data.name || slug,
      summary: data.summary || data.excerpt || data.description || '',
      image: sanitizePreviewImage(data.image || (Array.isArray(data.images) ? data.images[0] : null)),
    })
  }
  return result
}

async function fetchContentEntry(section, slug) {
  if (!slug) return null
  try {
    const url = resolveUrl(`content/${section}/${slug}.json`)
    const res = await fetch(url, { cache: 'no-store' })
    if (!res.ok) return null
    return await res.json()
  } catch (_) {
    return null
  }
}

let previewUsersMap = null
async function getPreviewUsersMap() {
  if (previewUsersMap) return previewUsersMap
  try {
    const url = resolveUrl('content/users.json')
    const res = await fetch(url, { cache: 'no-store' })
    if (!res.ok) {
      previewUsersMap = {}
      return previewUsersMap
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
    previewUsersMap = map
    return previewUsersMap
  } catch (_) {
    previewUsersMap = {}
    return previewUsersMap
  }
}

async function loadPreviewContacts(slugs) {
  if (!Array.isArray(slugs) || !slugs.length) return []
  const userMap = await getPreviewUsersMap()
  const entries = []
  for (const slug of slugs.slice(0, MAX_CONTACTS)) {
    const user = userMap[slug]
    if (!user) continue
    entries.push({
      id: slug,
      name: user.name || user.displayName || slug,
      email: user.email || '',
      title: user.title || user.role || '',
      image: sanitizePreviewImage(user.photo || user.image || ''),
    })
  }
  return entries
}

onBeforeUnmount(() => {
  cleanupPreviewResources()
})
</script>

<style scoped>
.wizard-shell {
  display: flex;
  justify-content: center;
}

.wizard {
  width: min(880px, 100%);
  padding: 32px 36px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.wizard-header h1 {
  margin: 8px 0;
  font-size: clamp(2rem, 3vw, 2.4rem);
}

.muted.helper {
  margin-top: 8px;
  font-size: 0.9rem;
}

.small-print {
  font-size: 0.85rem;
}

.wizard-form,
.review {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field input,
.field textarea,
.field select {
  font: inherit;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid #d0d0d8;
  background: #fff;
  color: inherit;
}

.field textarea {
  resize: vertical;
  min-height: 130px;
}

.field.checkbox {
  justify-content: flex-end;
}

.field.checkbox label {
  display: flex;
  gap: 8px;
  font-size: 0.95rem;
  align-items: center;
}

.type-fieldset,
.image-fieldset {
  border: 1px solid #d0d0d8;
  border-radius: 12px;
  padding: 16px 18px;
}

.type-fieldset legend,
.image-fieldset legend {
  padding: 0 8px;
  font-weight: 600;
}

.type-options,
.image-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 0.95rem;
}

.type-options label,
.image-options label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.image-entry {
  border: 1px dashed rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.6);
}

.image-entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.image-entry-title {
  font-weight: 600;
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.btn-icon {
  border: none;
  background: rgba(0, 0, 0, 0.06);
  color: #333;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
  line-height: 1;
}

.btn-icon:hover {
  background: rgba(0, 0, 0, 0.12);
}

.add-image-btn {
  margin-top: 10px;
  align-self: flex-start;
  padding: 8px 16px;
}

.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7, 10, 18, 0.62);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 16px;
  z-index: 1100;
  overflow-y: auto;
}

.preview-dialog {
  background: #ffffff;
  border-radius: 18px;
  width: min(960px, 100%);
  max-height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  box-shadow: 0 18px 46px rgba(12, 18, 38, 0.28);
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 1;
}

.preview-header .muted.small {
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.preview-title {
  margin: 4px 0 0;
  font-size: 1.35rem;
}

.btn-icon.close {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  font-size: 22px;
  line-height: 1;
  background: rgba(0, 0, 0, 0.06);
  color: #1a1a1f;
}

.btn-icon.close:hover {
  background: rgba(0, 0, 0, 0.12);
}

.preview-scroll {
  padding-bottom: 32px;
  overflow-y: auto;
}

.preview-scroll .section {
  padding-inline: 24px;
}

.preview-detail .container {
  max-width: 860px;
  margin-inline: auto;
}

.preview-scroll .status {
  padding: 36px;
  text-align: center;
}

.preview-detail .gallery {
  margin-top: 18px;
}

.preview-detail .video-wrap {
  position: relative;
  padding-top: 56.25%;
  margin-top: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2);
}

.preview-detail .video-wrap iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}

.preview-detail .meta {
  margin-top: 12px;
}

.preview-detail .meta strong {
  font-weight: 600;
}

.preview-detail .visit {
  margin-top: 16px;
}

.preview-detail .people {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.preview-detail .person {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-detail .avatar {
  height: 160px;
  border-radius: 12px;
  background-size: cover;
  background-position: center;
  background-color: #e9e9ee;
}

.preview-detail .related .cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.preview-detail .card.project {
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

.preview-detail .card.project .img {
  height: 180px;
  background: #ddd center/cover no-repeat;
}

.preview-detail .card.project .body {
  padding: 14px 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-detail .card.project .more {
  color: var(--cta-f26a2e);
  font-weight: 600;
}

@media (max-width: 900px) {
  .preview-overlay {
    padding: 20px 12px;
  }
  .preview-dialog {
    max-height: calc(100vh - 40px);
  }
  .preview-scroll .section {
    padding-inline: 16px;
  }
  .preview-detail .related .cards {
    grid-template-columns: 1fr;
  }
}

.file-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.06);
  font-size: 0.9rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  cursor: pointer;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.btn-primary {
  background: var(--cta-f26a2e);
  color: var(--unnamed-color-ffffff);
}

.btn-secondary {
  background: rgba(0, 0, 0, 0.06);
  color: inherit;
}

.btn-primary[disabled],
.btn-secondary[disabled] {
  opacity: 0.6;
  cursor: default;
}

.alert {
  border-radius: 8px;
  padding: 14px 16px;
  font-size: 0.95rem;
}

.alert.error {
  background: rgba(207, 62, 62, 0.14);
  color: #721515;
}

.alert.success {
  background: rgba(52, 168, 83, 0.14);
  color: #176232;
}

.alert.info {
  background: rgba(52, 152, 219, 0.14);
  color: #0f4a6a;
}

.selection-field {
  gap: 12px;
}

.selection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e0e0e6;
  border-radius: 8px;
  padding: 12px;
  background: #fafafa;
}

.selection-option {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
}

.option-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.selection-option input {
  flex-shrink: 0;
}

.selection-option .small {
  font-size: 0.85rem;
}

.connection {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 160ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .wizard {
    padding: 26px 22px;
  }

  .type-options,
  .image-options {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
