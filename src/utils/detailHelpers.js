import { sanitizeSrc, sanitizeUrl, isValidSlug } from './sanitize'
import { resolveUrl } from './paths.js'
import { ensureYouTubeEmbed } from './video'

/**
 * Normalize an image path for display.
 * Returns sanitized URL or null if invalid.
 *
 * @param {string|null} value - The raw image path
 * @returns {string|null} - Sanitized image path or null
 */
export function normalizeImage(value) {
  if (!value) return null
  return sanitizeSrc(resolveUrl(value))
}

/**
 * Normalize a video URL to YouTube embed format.
 * Returns sanitized embed URL or null if invalid.
 *
 * @param {string|null} value - The raw video URL
 * @returns {string|null} - YouTube embed URL or null
 */
export function normalizeVideo(value) {
  if (!value) return null
  const embed = ensureYouTubeEmbed(value)
  if (!embed) return null
  return sanitizeSrc(embed)
}

/**
 * Normalize a link URL for safe usage.
 * Returns sanitized URL, relative URL, or empty string if invalid.
 *
 * @param {string|null} value - The raw link URL
 * @returns {string} - Sanitized URL or empty string
 */
export function normalizeLink(value) {
  if (!value) return ''
  const trimmed = value.trim()
  if (!trimmed || trimmed === '#') return ''
  const resolved = resolveUrl(trimmed)
  if (typeof resolved !== 'string') return ''
  return resolved.startsWith('/') ? resolved : sanitizeUrl(resolved)
}

/**
 * Check if a URL is an external link (http/https).
 *
 * @param {string} value - The URL to check
 * @returns {boolean} - True if external, false otherwise
 */
export function isExternalLink(value) {
  return /^https?:\/\//i.test(value)
}

/**
 * Normalize an array of paper URLs.
 *
 * @param {Array|null} value - Array of paper URLs
 * @returns {Array<string>} - Array of normalized URLs
 */
export function normalizePapers(value) {
  if (!Array.isArray(value)) return []
  return value.map((entry) => normalizeLink(entry)).filter(Boolean)
}

/**
 * Parse body content into paragraphs.
 * Handles both string and array formats.
 *
 * @param {string|Array|null} body - The body content
 * @returns {Array<string>} - Array of paragraph strings
 */
export function parseBodyParagraphs(body) {
  if (!body) return []
  if (Array.isArray(body)) return body
  return String(body).split(/\n\n+/).map(s => s.trim()).filter(Boolean)
}

/**
 * Get and validate slug from URL search params.
 * Logs error if invalid slug detected.
 *
 * @returns {{slug: string|null, isValid: boolean}} - Slug and validation result
 */
export function getValidSlug() {
  const params = new URLSearchParams(location.search)
  const slug = params.get('slug')

  if (slug && !isValidSlug(slug)) {
    console.error('Invalid slug parameter')
    return { slug: null, isValid: false }
  }

  return { slug, isValid: Boolean(slug) }
}

// Cache for users data
let usersCache = null

/**
 * Load and cache the users map from JSON.
 * Returns a map of user slug/id to user data.
 *
 * @returns {Promise<Object>} - Map of user identifiers to user data
 */
export async function loadUsersMap() {
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

/**
 * Process raw image data into ordered arrays with captions.
 * Handles headline image placement at the beginning.
 *
 * @param {Object} data - The raw data object with image/images/imageCaptions
 * @returns {{images: Array<string>, captions: Array<string>, headlineImage: string|null}}
 */
export function processImages(data) {
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

  return {
    images: orderedImages,
    captions: normalizedCaptions,
    headlineImage
  }
}

/**
 * Fetch contacts data for given slugs.
 *
 * @param {Array<string>} contactSlugs - Array of contact slugs to fetch
 * @param {number} maxContacts - Maximum number of contacts to return
 * @returns {Promise<Array<Object>>} - Array of contact objects
 */
export async function fetchContacts(contactSlugs, maxContacts = 2) {
  if (!Array.isArray(contactSlugs) || !contactSlugs.length) return []

  const slugsToFetch = contactSlugs.slice(0, maxContacts)
  const userMap = await loadUsersMap()

  return slugsToFetch.map((refSlug) => {
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
}

/**
 * Fetch related items for a given content type.
 *
 * @param {Array<string>} relatedSlugs - Array of related item slugs
 * @param {string} contentPath - Base path for content (e.g., 'content/projects')
 * @param {number} maxItems - Maximum number of items to fetch
 * @returns {Promise<Array<Object>>} - Array of related item objects
 */
export async function fetchRelatedItems(relatedSlugs, contentPath, maxItems = 3) {
  if (!Array.isArray(relatedSlugs) || !relatedSlugs.length) return []

  const slugsToFetch = relatedSlugs.slice(0, maxItems)
  const results = await Promise.all(
    slugsToFetch.map(async (refSlug) => {
      try {
        const refRes = await fetch(resolveUrl(`${contentPath}/${refSlug}.json`), { cache: 'default' })
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
  return results.filter(Boolean)
}
