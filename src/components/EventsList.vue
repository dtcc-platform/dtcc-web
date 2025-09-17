<template>
  <main>
    <!-- Intro gradient section -->
    <section class="section gradient-sunrise intro">
      <div class="container grid2">
        <div>
          <h1 class="h2-50">Event landing:<br>Some upcoming events</h1>
        </div>
        <div>
          <p class="brodtext-20 muted">
            Placeholder event description text. Optatem repe sunt. Evelessi arunt eum fugiam, quodissera preheni ut et quis nullacc
            ullorat enim ut exerati antis dolor assinent exeria et arum faccum et es eume esed mo to eum aut molore ullorest, eic
            totas aut aque volorum que prat plam quiate cumquide cum idelect emquaceabor miliat volut id ut quas dollad volupat
            arum is volocatur, inus et aut qui rerist harum.
          </p>
        </div>
      </div>
    </section>

    <section class="section gradient-sunrise list">
      <div class="container">
        <div class="rows">
          <a class="row" v-for="e in items" :key="e.id" :href="detailHref(e.id)">
            <div class="title h3-30" v-text="e.title" />
            <div class="meta brodtext-20 muted" v-text="formatMeta(e)" />
          </a>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'

import { withBase } from '../utils/paths.js'
const items = ref([])

const suffixDay = (n) => {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return s[(v - 20) % 10] || s[v] || s[0]
}

function formatMeta(e) {
  if (e.meta) return e.meta
  try {
    const d = new Date(e.date)
    const m = d.toLocaleString(undefined, { month: 'long' })
    const day = d.getDate()
    const start = e.timeStart || ''
    const end = e.timeEnd || ''
    const time = start && end ? `${start}–${end}` : start || end || ''
    const loc = e.location || ''
    return [ `${m} ${day}${suffixDay(day)}`, time, loc ].filter(Boolean).join(', ')
  } catch (_) { return e.location || '' }
}

function detailHref(slug) {
  return withBase(`events/detail.html?slug=${encodeURIComponent(slug)}`)
}

onMounted(async () => {
  try {
    const r = await fetch(withBase('content/events/index.json'), { cache: 'no-store' })
    if (!r.ok) return
    const payload = await r.json()
    const arr = Array.isArray(payload.items) ? payload.items : Array.isArray(payload) ? payload : []
    const normalized = arr.map((it) => (typeof it === 'string' ? { id: it } : { id: it.id || it.slug || it.base, ...it }))
    normalized.sort((a, b) => (Date.parse(a.date) || 0) - (Date.parse(b.date) || 0))
    items.value = normalized
  } catch (_) {}
})
</script>

<style scoped>
.intro { padding-top: 36px; }
.grid2 { display: grid; grid-template-columns: .9fr 1.1fr; gap: 28px; align-items: start; }

.rows { margin-top: 6px; }
.row { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; padding: 18px 6px; border-bottom: 1px solid rgba(0,0,0,0.2); color: inherit; text-decoration: none; }
.row:hover { background: rgba(255,255,255,0.4); }
.title { color: var(--unnamed-color-27252a); }
.meta { text-align: right; }

@media (max-width: 900px) {
  .grid2 { grid-template-columns: 1fr; }
  .row { grid-template-columns: 1fr; }
  .meta { text-align: left; }
}
</style>
