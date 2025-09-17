<template>
  <div class="wizard-shell container">
    <section class="wizard card">
      <header class="wizard-header">
        <p class="eyebrow">Internal tool</p>
        <h1>News Draft Wizard</h1>
        <p class="muted">
          Draft runtime news entries directly in the browser. Supply a Gemini API key (kept only in
          this session), review the generated JSON, and save it into <code>public/content/news</code>.
        </p>
        <p class="muted small-print">
          The workflow is experimental and runs entirely client-side. Double-check every output before
          sharing or committing the changes.
        </p>
      </header>

      <form class="wizard-form" @submit.prevent="generateDraft">
        <div class="field">
          <label for="api-key">Gemini API key<span aria-hidden="true">*</span></label>
          <input
            id="api-key"
            v-model="apiKey"
            type="password"
            placeholder="AIza..."
            autocomplete="off"
            required
          >
          <p class="muted helper">Stored in memory only; page refresh clears it.</p>
        </div>

        <div class="field">
          <label for="headline">Headline<span aria-hidden="true">*</span></label>
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
          <label for="bullets">Supporting bullet points<span aria-hidden="true">*</span></label>
          <textarea
            id="bullets"
            v-model="bulletInput"
            rows="4"
            placeholder="One detail per line"
            required
          ></textarea>
          <p class="muted helper">Each line becomes a bullet passed to Gemini.</p>
        </div>

        <div class="split-fields">
          <div class="field">
            <label for="slug">Slug</label>
            <input
              id="slug"
              v-model="slug"
              type="text"
              autocomplete="off"
              @input="slugWasEdited = true"
            >
            <p class="muted helper">Used for filenames and /news/&lt;slug&gt; URLs.</p>
          </div>
          <div class="field">
            <label for="tone">Tone guidance</label>
            <input
              id="tone"
              v-model="tone"
              type="text"
              placeholder="e.g. focused, celebratory"
              autocomplete="off"
            >
          </div>
          <div class="field">
            <label for="model">Model</label>
            <input
              id="model"
              v-model="model"
              type="text"
              autocomplete="off"
            >
            <p class="muted helper">Defaults to Gemini 1.5 Pro.</p>
          </div>
        </div>

        <div class="actions">
          <button type="submit" class="btn-primary" :disabled="isDrafting">
            <span v-if="isDrafting">Creating draft…</span>
            <span v-else>Generate draft</span>
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

          <div class="split-fields">
            <div class="field">
              <label for="manifest-image">Manifest image override</label>
              <input
                id="manifest-image"
                v-model="manifestImage"
                type="text"
                placeholder="Leave blank to use the draft image"
              >
            </div>
            <div class="field checkbox">
              <label>
                <input type="checkbox" v-model="forceOverwrite">
                Allow overwrite if the JSON file already exists
              </label>
            </div>
          </div>

          <div v-if="fsSupported" class="connection">
            <p class="muted">
              Repository folder: <strong>{{ repoLabel || 'not connected' }}</strong>
            </p>
            <button class="btn-secondary" type="button" @click="connectRepository">
              {{ repoLabel ? 'Change folder' : 'Connect repository folder' }}
            </button>
            <p class="muted helper">Choose the repo root containing <code>public/content/news</code>.</p>
          </div>
          <div v-else class="alert info">
            Your browser does not support the File System Access API. Use “Download JSON” and copy
            the file into <code>public/content/news</code> manually.
          </div>

          <div class="actions">
            <button class="btn-primary" type="button" :disabled="isSaving" @click="publishDraft">
              <span v-if="isSaving">Saving…</span>
              <span v-else>Save to repository</span>
            </button>
            <button class="btn-secondary" type="button" :disabled="isSaving" @click="downloadDraft">
              Download JSON
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
import { computed, ref, watch } from 'vue'

const title = ref('')
const bulletInput = ref('')
const slug = ref('')
const slugWasEdited = ref(false)
const tone = ref('')
const model = ref(import.meta.env.VITE_GEMINI_MODEL || 'gemini-1.5-pro')
const apiKey = ref('')
const manifestImage = ref('')
const draftJson = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const forceOverwrite = ref(false)
const isDrafting = ref(false)
const isSaving = ref(false)
const repoLabel = ref('')
const rootHandle = ref(null)

const fsSupported = typeof window !== 'undefined' && 'showDirectoryPicker' in window

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

const hasDraft = computed(() => Boolean(draftJson.value.trim()))

function parseBullets() {
  return bulletInput.value
    .split(/\r?\n/g)
    .map((line) => line.trim())
    .filter(Boolean)
}

function slugify(value = '') {
  return value
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || 'news-entry'
}

function buildPrompt({ title, bulletText, slugValue, toneValue }) {
  const toneClause = toneValue
    ? `Match this tone: ${toneValue}.`
    : 'Maintain the professional-yet-approachable tone of an architectural firm.'
  return `You help prepare runtime news items for the DTCC marketing site.\n` +
    'Follow the "DTCC Web — Content Posting Guide" requirements for public/content/news/*.json entries.\n\n' +
    'Constraints:\n' +
    '- Output must be a single JSON object compatible with JSON.parse.\n' +
    '- Include keys only when they offer value. Required key: "title".\n' +
    '- Prefer ISO date format (YYYY-MM-DD) when a specific date is implied.\n' +
    `- Use the provided slug ${slugValue} to build any internal URLs (e.g. "/news/${slugValue}").\n` +
    '- Suggest an image URL under the `image` key if you can reference a relevant royalty-free photograph.\n' +
    '- Limit the summary to ~40 words.\n' +
    `- ${toneClause}\n\n` +
    `Inputs:\n- Headline: ${title}\n- Supporting details:\n${bulletText}\n\n` +
    'Return only the JSON object, nothing else.'
}

function extractTextPayload(response) {
  const candidates = response?.candidates
  if (!Array.isArray(candidates) || candidates.length === 0) return ''
  const parts = candidates[0]?.content?.parts
  if (!Array.isArray(parts)) return ''
  return parts
    .map((part) => part?.text || '')
    .join('\n')
    .trim()
}

async function generateDraft() {
  errorMessage.value = ''
  successMessage.value = ''

  const key = apiKey.value.trim()
  if (!key) {
    errorMessage.value = 'Add your Gemini API key before generating a draft.'
    return
  }

  const bullets = parseBullets()
  if (!title.value.trim() || bullets.length === 0) {
    errorMessage.value = 'Provide a headline and at least one supporting bullet.'
    return
  }

  isDrafting.value = true
  const slugValue = slug.value.trim() || slugify(title.value)
  const bulletText = bullets.map((line) => `- ${line}`).join('\n')
  const prompt = buildPrompt({
    title: title.value.trim(),
    bulletText,
    slugValue,
    toneValue: tone.value.trim(),
  })

  try {
    const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${model.value}:generateContent?key=${encodeURIComponent(key)}`
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 0.45,
          responseMimeType: 'application/json',
        },
      }),
    })

    const payload = await response.json()
    if (!response.ok) {
      const message = payload?.error?.message || response.statusText
      throw new Error(message)
    }

    const text = extractTextPayload(payload)
    if (!text) {
      throw new Error('Gemini returned an empty response.')
    }

    let parsed
    try {
      parsed = JSON.parse(text)
    } catch (err) {
      throw new Error('Gemini returned data that is not valid JSON.')
    }

    slug.value = slugValue
    slugWasEdited.value = true
    draftJson.value = JSON.stringify(parsed, null, 2)
    manifestImage.value = parsed?.image || ''
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

async function getNewsDirectory(root) {
  try {
    const publicDir = await root.getDirectoryHandle('public')
    const contentDir = await publicDir.getDirectoryHandle('content')
    return await contentDir.getDirectoryHandle('news')
  } catch (err) {
    throw new Error('Selected folder must contain public/content/news/.')
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

function manifestContains(items, slugValue) {
  return items.some((entry) => {
    if (typeof entry === 'string') return entry === slugValue
    return entry && typeof entry === 'object' && entry.base === slugValue
  })
}

async function updateManifest(newsDir, slugValue, image, { force }) {
  let handle
  try {
    handle = await newsDir.getFileHandle('index.json')
  } catch (err) {
    if (err?.name === 'NotFoundError') {
      handle = await newsDir.getFileHandle('index.json', { create: true })
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

  const alreadyPresent = manifestContains(manifest.items, slugValue)
  if (!alreadyPresent) {
    const entry = image ? { base: slugValue, image } : { base: slugValue }
    manifest.items.push(entry)
  } else if (force && image) {
    manifest.items = manifest.items.map((entry) =>
      (typeof entry === 'string' ? (entry === slugValue ? { base: slugValue, image } : entry)
        : entry?.base === slugValue ? { ...entry, image } : entry)
    )
  }

  const writer = await handle.createWritable()
  await writer.write(`${JSON.stringify(manifest, null, 2)}\n`)
  await writer.close()

  return !alreadyPresent
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

  const slugValue = slug.value.trim() || slugify(title.value)

  if (!fsSupported) {
    errorMessage.value = 'Saving requires a browser with File System Access support. Use “Download JSON” instead.'
    return
  }

  isSaving.value = true
  try {
    const root = await ensureRepoHandle()
    const newsDir = await getNewsDirectory(root)

    await writeJsonFile(newsDir, `${slugValue}.json`, parsed, { force: forceOverwrite.value })

    const image = manifestImage.value.trim() || parsed.image || undefined
    const added = await updateManifest(newsDir, slugValue, image, { force: forceOverwrite.value })

    successMessage.value = `Saved public/content/news/${slugValue}.json${added ? ' and updated index.json.' : '.'}`
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
  } finally {
    isSaving.value = false
  }
}

function downloadDraft() {
  if (!hasDraft.value) return

  const fileSlug = slug.value.trim() || slugify(title.value)
  const blob = new Blob([draftJson.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${fileSlug}.json`
  anchor.click()
  URL.revokeObjectURL(url)
}

function resetWizard() {
  title.value = ''
  bulletInput.value = ''
  slug.value = ''
  slugWasEdited.value = false
  tone.value = ''
  manifestImage.value = ''
  draftJson.value = ''
  successMessage.value = ''
  errorMessage.value = ''
  forceOverwrite.value = false
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
.field textarea {
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

.split-fields {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
}
</style>
