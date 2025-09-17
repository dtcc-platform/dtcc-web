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
