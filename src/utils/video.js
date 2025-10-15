const YOUTUBE_HOSTS = new Set([
  'youtube.com',
  'www.youtube.com',
  'm.youtube.com',
  'youtu.be',
  'www.youtu.be',
])

export function toYouTubeEmbed(rawUrl = '') {
  const trimmed = rawUrl?.trim()
  if (!trimmed) return ''
  return extractEmbed(trimmed)
}

export function ensureYouTubeEmbed(value) {
  if (!value) return ''
  if (typeof value !== 'string') return ''
  const trimmed = value.trim()
  if (!trimmed) return ''

  // Already an embed URL
  if (/^https?:\/\/(www\.)?youtube\.com\/embed\//i.test(trimmed)) {
    return trimmed
  }

  return extractEmbed(trimmed)
}

function extractEmbed(input) {
  let url
  try {
    url = new URL(normalizeScheme(input))
  } catch (_) {
    return ''
  }

  const host = url.hostname.toLowerCase()
  if (!YOUTUBE_HOSTS.has(host)) return ''

  let videoId = ''
  let startSeconds = extractStartSeconds(url)

  if (host.includes('youtu.be')) {
    videoId = url.pathname.replace(/^\/+/, '').split(/[/?#]/, 1)[0]
  } else if (url.pathname.startsWith('/watch')) {
    videoId = url.searchParams.get('v') || ''
  } else if (url.pathname.startsWith('/shorts/')) {
    videoId = url.pathname.split('/')[2] || ''
  } else if (url.pathname.startsWith('/embed/')) {
    videoId = url.pathname.split('/')[2] || ''
  } else if (url.pathname.startsWith('/live/')) {
    videoId = url.pathname.split('/')[2] || ''
  }

  if (!videoId) return ''

  const query = startSeconds > 0 ? `?start=${startSeconds}` : ''
  return `https://www.youtube.com/embed/${videoId}${query}`
}

function normalizeScheme(value) {
  if (/^[a-z]+:\/\//i.test(value)) return value
  return `https://${value}`
}

function extractStartSeconds(url) {
  const params = url.searchParams
  const candidates = [params.get('start'), params.get('t')]
  for (const candidate of candidates) {
    const seconds = parseTimestamp(candidate)
    if (seconds > 0) return seconds
  }
  if (url.hash) {
    const hash = url.hash.replace(/^#/, '')
    if (hash.startsWith('t=')) {
      const seconds = parseTimestamp(hash.slice(2))
      if (seconds > 0) return seconds
    }
  }
  return 0
}

function parseTimestamp(value) {
  if (!value) return 0
  if (/^\d+$/.test(value)) return Number(value)
  const match = value.match(/(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?/i)
  if (!match) return 0
  const [, hours = '0', minutes = '0', seconds = '0'] = match
  const total = Number(hours) * 3600 + Number(minutes) * 60 + Number(seconds)
  return Number.isFinite(total) ? total : 0
}
