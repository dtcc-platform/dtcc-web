<template>
  <section class="section social-feed">
    <div class="container">
      <header class="feed-header">
        <h2 class="h3-30">From LinkedIn</h2>
        <a :href="companyUrl" target="_blank" rel="noopener" class="more">Visit our LinkedIn page »</a>
      </header>
      <p class="intro muted">Latest highlights and announcements from the Digital Twin Cities Centre community.</p>

      <div v-if="isLoading" class="status muted">Loading feed…</div>
      <div v-else-if="errorMessage" class="alert error">{{ errorMessage }}</div>
      <div v-else-if="!displayedPosts.length" class="status muted">No recent posts available. Check back soon.</div>
      <div v-else class="cards">
        <article v-for="post in displayedPosts" :key="post.id" class="card">
          <div class="media" :class="{ placeholder: !post.image }" :style="post.image ? { backgroundImage: `url(${post.image})` } : undefined"></div>
          <div class="body">
            <p class="meta">{{ post.published }}</p>
            <p class="summary">{{ post.summary }}</p>
            <a class="more" :href="post.url" target="_blank" rel="noopener">Read on LinkedIn »</a>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { withBase, resolveUrl } from '../utils/paths'
import { sanitizeSrc, sanitizeUrl } from '../utils/sanitize'

const FEED_PATH = 'content/social/linkedin_posts_complete.json'
const MAX_POSTS = 6
const companyUrl = 'https://www.linkedin.com/company/digital-twin-cities-centre/'

const isLoading = ref(true)
const errorMessage = ref('')
const posts = ref([])

onMounted(async () => {
  try {
    const response = await fetch(withBase(FEED_PATH), { cache: 'no-store' })
    if (!response.ok) {
      throw new Error(`Unable to load LinkedIn feed (${response.status})`)
    }
    const payload = await response.json()
    const rawPosts = Array.isArray(payload?.posts) ? payload.posts : []
    const mapped = rawPosts
      .map(normalizePost)
      .filter((post) => post.summary || post.image)
    posts.value = mapped.slice(0, MAX_POSTS)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
  } finally {
    isLoading.value = false
  }
})

const displayedPosts = computed(() => posts.value)

function normalizePost(raw = {}) {
  const textSource = raw.commentary || raw.original_data?.commentary || ''
  const summary = truncate(toPlainText(String(textSource || '')), 220)
  const publishedTs = raw.published_at || raw.original_data?.publishedAt || raw.original_data?.createdAt || null
  const imageUrl = raw.media?.image_url || null
  const link = raw.post_url || (raw.post_id ? `https://www.linkedin.com/feed/update/${raw.post_id}/` : null)

  return {
    id: raw.post_id || raw.original_data?.id || cryptoRandomId(),
    url: sanitizeUrl(link || companyUrl),
    published: formatDate(publishedTs),
    image: imageUrl ? sanitizeSrc(resolveUrl(imageUrl)) : null,
    summary,
  }
}

function toPlainText(value) {
  if (!value) return ''
  let text = value
    .replace(/@\[(.*?)\]\([^\)]+\)/g, '$1')
    .replace(/https?:\/\/\S+/g, (match) => match)
    .replace(/\n+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  return text
}

function truncate(text, limit) {
  if (!text) return ''
  if (text.length <= limit) return text
  return `${text.slice(0, limit).trimEnd()}…`
}

function formatDate(timestamp) {
  if (!timestamp) return 'Recently'
  const date = new Date(Number(timestamp))
  if (Number.isNaN(date.getTime())) return 'Recently'
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function cryptoRandomId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `temp-${Math.random().toString(36).slice(2)}`
}
</script>

<style scoped>
.social-feed { padding-block: 60px; }
.feed-header { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; margin-bottom: 10px; }
.intro { margin-bottom: 24px; font-size: 1rem; }
.status { padding: 18px; border-radius: 10px; background: rgba(0, 0, 0, 0.04); }
.alert { padding: 18px; border-radius: 10px; font-weight: 500; }
.alert.error { background: rgba(207, 62, 62, 0.12); color: #6d1a1a; }
.cards { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.card { display: flex; flex-direction: column; border-radius: 14px; overflow: hidden; background: #fff; box-shadow: 0 6px 22px rgba(0, 0, 0, 0.08); }
.media { height: 180px; background: #1b2a4a center/cover no-repeat; }
.media.placeholder { background: linear-gradient(135deg, #24385f, #152240); }
.body { padding: 18px 20px 22px; display: flex; flex-direction: column; gap: 12px; flex: 1; }
.meta { font-size: 0.85rem; color: #6c6c74; text-transform: uppercase; letter-spacing: 0.08em; }
.summary { font-size: 1rem; line-height: 1.5; color: #1b1b1f; }
.more { color: var(--cta-f26a2e); font-weight: 600; text-decoration: none; }
.more:hover { text-decoration: underline; }
@media (max-width: 700px) {
  .feed-header { flex-direction: column; align-items: flex-start; }
}
</style>
