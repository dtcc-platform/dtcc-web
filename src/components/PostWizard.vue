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

        <div v-if="postType !== 'events'" class="field related-field">
          <label>Related {{ postType === 'projects' ? 'projects' : 'news items' }}</label>
          <p class="muted helper">Select up to {{ MAX_RELATED }} related entries to feature alongside this post.</p>
          <div v-if="relatedLoading" class="muted helper">Loading related options…</div>
          <div v-else-if="relatedError" class="alert error">{{ relatedError }}</div>
          <div v-else class="related-options">
            <label v-for="option in relatedOptions" :key="option.slug" class="related-option">
              <input
                type="checkbox"
                :checked="isRelatedSelected(option.slug)"
                :disabled="!isRelatedSelected(option.slug) && relatedSelectionFull"
                @change="toggleRelated(option.slug, $event.target.checked)"
              >
              <span>{{ option.title }}</span>
            </label>
            <p v-if="!relatedOptions.length" class="muted helper">No existing entries available yet.</p>
          </div>
        </div>

        <fieldset class="field image-fieldset">
          <legend>Image</legend>
          <div class="image-options">
            <label>
              <input type="radio" value="none" v-model="imageSource">
              No image
            </label>
            <label>
              <input type="radio" value="url" v-model="imageSource">
              Link to an online image
            </label>
            <label>
              <input type="radio" value="upload" v-model="imageSource">
              Upload from your computer
            </label>
          </div>

          <div class="field" v-if="imageSource === 'url'">
            <label for="image-url">Image URL</label>
            <input
              id="image-url"
              v-model="imageUrl"
              type="url"
              placeholder="https://images.unsplash.com/..."
              autocomplete="off"
            >
            <p class="muted helper">Remote URLs are stored directly in the JSON and manifest.</p>
          </div>

          <div class="field" v-else-if="imageSource === 'upload'">
            <label for="image-file">Select image</label>
            <input id="image-file" type="file" accept="image/*" @change="onImageFileChange">
            <p class="muted helper">
              Saved next to the JSON as <code>{{ computedImagePath }}</code>. Recommended size ≥ 1200px wide.
            </p>
            <p v-if="imageFileName" class="file-pill">{{ imageFileName }}</p>
          </div>
        </fieldset>

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
          <p class="muted helper">{{ saveTargetNote }}</p>

          <div class="field checkbox">
            <label>
              <input type="checkbox" v-model="forceOverwrite">
              Allow overwrite if the JSON file already exists
            </label>
          </div>

          <div v-if="remotePublishEnabled" class="alert info">
            Publishing uses the configured API endpoint. The JSON (and optional image) will be committed
            via the serverless workflow after you sign in.
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
            <button class="btn-primary" type="button" :disabled="isSaving" @click="publishDraft">
              <span v-if="isSaving">Saving…</span>
              <span v-else>Save to repository</span>
            </button>
            <button class="btn-secondary" type="button" :disabled="isSaving" @click="downloadDraft">
              Download JSON{{ preparedImage.type === 'upload' && preparedImage.file ? ' & image' : '' }}
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
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'

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

const publishEndpoint = import.meta.env.VITE_CHAT_PUBLISH_URL?.trim() || ''
const remotePublishEnabled = computed(() => Boolean(publishEndpoint))
const authSession = inject('chatAuthSession', ref({ token: '', expiresAt: 0 }))
const authToken = inject('chatAuthToken', ref(''))
const basePath = (import.meta.env.BASE_URL || '/').replace(/\/$/, '')

const typeOptions = TYPE_OPTIONS

const postType = ref('news')
const title = ref('')
const bodyInput = ref('')
const slug = ref('')
const slugWasEdited = ref(false)
const selectedDate = ref(new Date().toISOString().slice(0, 10))
const MAX_RELATED = 3
const relatedOptions = ref([])
const relatedLoading = ref(false)
const relatedError = ref('')
const selectedRelated = ref([])
const relatedSelectionFull = computed(() => selectedRelated.value.length >= MAX_RELATED)

const imageSource = ref('none')
const imageUrl = ref('')
const imageFile = ref(null)
const imageFileName = ref('')
const imageFileExtension = ref('')

const preparedImage = ref({
  type: 'none',
  jsonValue: '',
  manifestValue: '',
  ext: '',
  file: null,
  section: postType.value,
})

const draftSection = ref(null)
const draftJson = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const forceOverwrite = ref(false)
const isDrafting = ref(false)
const isSaving = ref(false)
const repoLabel = ref('')
const rootHandle = ref(null)

const fsSupported = typeof window !== 'undefined' && 'showDirectoryPicker' in window

const sectionConfig = computed(() => SECTION_CONFIG[postType.value] || SECTION_CONFIG.news)
const contentSubdir = computed(() => sectionConfig.value.contentDir)
const currentTypeLabel = computed(() => sectionConfig.value.label)
const draftSectionLabel = computed(() =>
  draftSection.value ? (SECTION_CONFIG[draftSection.value]?.label || draftSection.value) : ''
)

const computedSlug = computed(() => slug.value.trim() || slugify(title.value))
const computedImagePath = computed(() => {
  const baseSlug = computedSlug.value || 'post-entry'
  const ext = imageFileExtension.value || inferExtensionFromName(imageFileName.value) || '.jpg'
  return `content/${contentSubdir.value}/${baseSlug}${ext}`
})

const hasDraft = computed(() => Boolean(draftJson.value.trim()))

const imageReviewNote = computed(() => {
  if (!hasDraft.value) return ''
  const state = preparedImage.value
  if (state.type === 'url' && state.manifestValue) {
    if (state.section !== postType.value) {
      return `Draft image points to ${state.manifestValue}. Regenerate the draft after switching to ${currentTypeLabel.value}.`
    }
    return `Using remote image ${state.manifestValue}.`
  }
  if (state.type === 'upload' && state.jsonValue) {
    if (state.section !== postType.value) {
      return `Draft image is set to ${state.jsonValue}. Regenerate the draft after switching to ${currentTypeLabel.value}.`
    }
    return `Image will be saved as ${state.jsonValue}.`
  }
  return 'No image selected. Manifest entry will omit an image reference.'
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

watch(imageSource, (mode) => {
  if (mode !== 'upload') {
    imageFile.value = null
    imageFileName.value = ''
    imageFileExtension.value = ''
  }
  if (mode !== 'url') {
    imageUrl.value = ''
  }
})

watch(postType, (section) => {
  selectedRelated.value = []
  refreshRelatedOptions(section)
})

onMounted(() => {
  refreshRelatedOptions(postType.value)
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

function createSummary(body) {
  if (!body) return ''
  const paragraph = body.split(/\n{2,}/)[0] || ''
  const condensed = paragraph.replace(/\s+/g, ' ').trim()
  if (!condensed) return ''
  if (condensed.length <= 180) return condensed
  return `${condensed.slice(0, 177).trimEnd()}…`
}

function onImageFileChange(event) {
  const file = event?.target?.files?.[0]
  if (!file) {
    imageFile.value = null
    imageFileName.value = ''
    imageFileExtension.value = ''
    return
  }
  imageFile.value = file
  imageFileName.value = file.name || 'uploaded-image'
  imageFileExtension.value = deriveExtension(file)
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

    let imageEntry = ''
    if (imageSource.value === 'url') {
      const remote = imageUrl.value.trim()
      if (remote) {
        imageEntry = remote
        preparedImage.value = {
          type: 'url',
          jsonValue: remote,
          manifestValue: remote,
          ext: '',
          file: null,
          section,
        }
      } else {
        preparedImage.value = { type: 'none', jsonValue: '', manifestValue: '', ext: '', file: null, section }
      }
    } else if (imageSource.value === 'upload') {
      const file = imageFile.value
      if (!file) {
        throw new Error('Select an image to upload or choose a different image option.')
      }
      const ext = imageFileExtension.value || deriveExtension(file) || '.jpg'
      const filename = `${slugValue}${ext}`
      imageEntry = `content/${contentDir}/${filename}`
      preparedImage.value = {
        type: 'upload',
        jsonValue: imageEntry,
        manifestValue: imageEntry,
        ext,
        file,
        section,
      }
    } else {
      preparedImage.value = { type: 'none', jsonValue: '', manifestValue: '', ext: '', file: null, section }
    }

    let payload
    if (section === 'events') {
      payload = {
        title: titleValue,
        summary,
        body: normalizedBody,
        date: isoDate,
      }
      if (imageEntry) payload.image = imageEntry
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
      if (imageEntry) payload.image = imageEntry
    } else {
      payload = {
        title: titleValue,
        summary,
        url: `${config.urlPrefix}${slugValue}`,
        body: normalizedBody,
        eyebrow: 'News',
        date: isoDate,
      }
      if (imageEntry) payload.image = imageEntry
    }

    if (postType.value !== 'events') {
      if (selectedRelated.value.length) {
        payload.related = [...selectedRelated.value]
      } else {
        delete payload.related
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
  } else {
    delete parsed.related
  }

  const slugValue = slug.value.trim() || slugify(parsed.title)
  slug.value = slugValue
  slugWasEdited.value = true

  const section = postType.value
  const config = SECTION_CONFIG[section] || SECTION_CONFIG.news

  const uploadState = preparedImage.value.type === 'upload' && preparedImage.value.file
    ? preparedImage.value
    : null

  if (uploadState) {
    const ext = uploadState.ext || deriveExtension(uploadState.file) || '.jpg'
    const expectedPrefix = `content/${config.contentDir}/`
    let imagePath = typeof parsed.image === 'string' ? parsed.image.trim() : ''
    if (!imagePath || uploadState.section !== section || !imagePath.startsWith(expectedPrefix)) {
      imagePath = `${expectedPrefix}${slugValue}${ext}`
    }
    if (!imagePath.startsWith(expectedPrefix)) {
      errorMessage.value = `Uploaded image path must live under ${expectedPrefix}. Update the JSON before saving.`
      return
    }
    parsed.image = imagePath
  }

  const manifestImage = section === 'events' ? '' : (typeof parsed.image === 'string' ? parsed.image.trim() : '')
  const commitMessage = buildCommitMessage(section, slugValue)

  isSaving.value = true
  try {
    if (remotePublishEnabled.value) {
      await publishViaApi({ parsed, slugValue, section, uploadState, config, commitMessage })
    } else {
      await publishToFileSystem({ parsed, slugValue, section, uploadState, config, manifestImage })
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

async function publishToFileSystem({ parsed, slugValue, section, uploadState, config, manifestImage }) {
  const root = await ensureRepoHandle()
  const sectionDir = await getContentDirectory(root, config.contentDir)

  await writeJsonFile(sectionDir, `${slugValue}.json`, parsed, { force: forceOverwrite.value })

  if (uploadState) {
    const expectedPrefix = `content/${config.contentDir}/`
    const imagePath = parsed.image
    const targetName = imagePath.startsWith(expectedPrefix)
      ? imagePath.slice(expectedPrefix.length)
      : `${slugValue}${uploadState.ext || '.jpg'}`
    await writeBinaryFile(sectionDir, targetName, uploadState.file, { force: forceOverwrite.value })
  }

  const added = await updateManifest(sectionDir, section, slugValue, parsed, manifestImage, { force: forceOverwrite.value })

  successMessage.value = `Saved public/content/${config.contentDir}/${slugValue}.json${added ? ' and updated index.json.' : '.'}`
  draftSection.value = section
  preparedImage.value = {
    ...preparedImage.value,
    section,
  }
}

async function publishViaApi({ parsed, slugValue, section, uploadState, config, commitMessage }) {
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

  if (uploadState) {
    const expectedPrefix = `content/${config.contentDir}/`
    const imagePath = typeof parsed.image === 'string' ? parsed.image.trim() : ''
    const filename = imagePath.startsWith(expectedPrefix)
      ? imagePath.slice(expectedPrefix.length)
      : `${slugValue}${uploadState.ext || '.jpg'}`
    body.imageUpload = {
      filename,
      contentType: uploadState.file.type || 'application/octet-stream',
      data: await fileToBase64(uploadState.file),
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
  preparedImage.value = {
    ...preparedImage.value,
    section,
  }
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

  if (preparedImage.value.type === 'upload' && preparedImage.value.file) {
    const config = sectionConfig.value
    const expectedPrefix = `content/${config.contentDir}/`
    let filename = preparedImage.value.jsonValue
    if (filename?.startsWith(expectedPrefix)) {
      filename = filename.slice(expectedPrefix.length)
    } else {
      filename = `${slugValue}${preparedImage.value.ext || '.jpg'}`
    }
    const imageUrl = URL.createObjectURL(preparedImage.value.file)
    const imageAnchor = document.createElement('a')
    imageAnchor.href = imageUrl
    imageAnchor.download = filename
    imageAnchor.click()
    URL.revokeObjectURL(imageUrl)
  }
}

function resetWizard() {
  title.value = ''
  bodyInput.value = ''
  slug.value = ''
  slugWasEdited.value = false
  selectedDate.value = new Date().toISOString().slice(0, 10)
  imageSource.value = 'none'
  imageUrl.value = ''
  imageFile.value = null
  imageFileName.value = ''
  imageFileExtension.value = ''
  preparedImage.value = { type: 'none', jsonValue: '', manifestValue: '', ext: '', file: null, section: postType.value }
  draftSection.value = null
  draftJson.value = ''
  successMessage.value = ''
  errorMessage.value = ''
  forceOverwrite.value = false
  selectedRelated.value = []
}
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

.related-field {
  gap: 12px;
}

.related-options {
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

.related-option {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
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
