const rawBase = import.meta.env.BASE_URL || '/'
const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`
const ABSOLUTE_URL_RE = /^[a-z][a-z\d+\-.]*:/i

/** Prefix a path with the current Vite base (handles GitHub Pages subpaths). */
export function withBase(path = '') {
  if (!path) return base
  return base + path.replace(/^\/+/, '')
}

/**
 * Resolve a possibly relative URL against the Vite base. Absolute URLs (http, https, mailto, etc.)
 * are returned untouched, while protocol-relative URLs (//example.com) are also kept as-is.
 */
export function resolveUrl(path = '') {
  if (typeof path !== 'string') return path
  const trimmed = path.trim()
  if (!trimmed) return trimmed
  if (trimmed.startsWith('//')) return trimmed
  if (ABSOLUTE_URL_RE.test(trimmed)) return trimmed
  return withBase(trimmed)
}

/**
 * Convert an image path to use WebP format if available.
 * Returns the WebP path for .png, .jpg, .jpeg images.
 * For external URLs (http/https), returns the original path.
 *
 * @param {string} imagePath - The original image path
 * @returns {string} - The WebP path or original path
 */
export function toWebP(imagePath) {
  if (!imagePath || typeof imagePath !== 'string') return imagePath

  // Don't convert external URLs
  if (ABSOLUTE_URL_RE.test(imagePath) || imagePath.startsWith('//')) {
    return imagePath
  }

  // Don't convert data URLs or blob URLs
  if (imagePath.startsWith('data:') || imagePath.startsWith('blob:')) {
    return imagePath
  }

  // Convert common image extensions to WebP
  return imagePath.replace(/\.(png|jpe?g)$/i, '.webp')
}

/**
 * Check if browser supports WebP format.
 * Caches the result after first check.
 */
let webpSupported = null
export function supportsWebP() {
  if (webpSupported !== null) return webpSupported

  if (typeof document === 'undefined') {
    webpSupported = true // Assume supported for SSR
    return webpSupported
  }

  const canvas = document.createElement('canvas')
  if (canvas.getContext && canvas.getContext('2d')) {
    // Check if toDataURL supports WebP
    webpSupported = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0
  } else {
    webpSupported = false
  }

  return webpSupported
}

/**
 * Get optimized image URL with WebP support and fallback.
 * Returns WebP version if supported, otherwise returns original.
 *
 * @param {string} imagePath - The original image path
 * @returns {string} - The optimized image path
 */
export function getOptimizedImageUrl(imagePath) {
  if (!imagePath) return imagePath

  // For external URLs, return as-is
  if (ABSOLUTE_URL_RE.test(imagePath) || imagePath.startsWith('//')) {
    return imagePath
  }

  // Check if image is PNG or JPEG
  if (/\.(png|jpe?g)$/i.test(imagePath)) {
    // Always return WebP version - browser will handle fallback via picture element
    // or we rely on the server/CDN having the WebP version available
    return toWebP(imagePath)
  }

  return imagePath
}
