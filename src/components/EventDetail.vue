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
    </section>

    <section class="section gradient-sunrise body">
      <div class="container grid2">
        <div>
          <h2 class="h3-30">Details</h2>
        </div>
        <div>
          <p class="brodtext-20 muted" v-for="(p, i) in bodyParas" :key="i" v-text="p" />
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sanitizeUrl } from '../utils/sanitize'
import { resolveUrl } from '../utils/paths.js'

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

onMounted(async () => {
  if (!slug) return
  try {
    const r = await fetch(resolveUrl(`content/events/${slug}.json`), { cache: 'no-store' })
    if (!r.ok) return
    const data = await r.json()
    item.value = {
      id: slug,
      title: data.title || slug,
      summary: data.summary || data.description || '',
      body: data.body || '',
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

.body { padding-top: 24px; padding-bottom: 24px; }

@media (max-width: 1000px) {
  .grid2 { grid-template-columns: 1fr; }
}
</style>
