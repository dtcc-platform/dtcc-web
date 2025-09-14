/** Basic URL sanitizer to avoid javascript: and other dangerous schemes. */
export function sanitizeUrl(input) {
  if (typeof input !== 'string' || !input.trim()) return '#'
  const url = input.trim()
  // Allow relative URLs
  if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) return url
  try {
    const u = new URL(url)
    const allowed = ['http:', 'https:'] // Reject data:, blob:, javascript:, etc.
    if (!allowed.includes(u.protocol)) return '#'
    return u.toString()
  } catch {
    return '#'
  }
}

/** Sanitize image/video src: allow only http(s) or relative. */
export function sanitizeSrc(input) {
  if (typeof input !== 'string' || !input.trim()) return null
  const url = input.trim()
  if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) return url
  try {
    const u = new URL(url)
    const allowed = ['http:', 'https:']
    if (!allowed.includes(u.protocol)) return null
    return u.toString()
  } catch {
    return null
  }
}

/** Escape all HTML then permit <br> tags back (simple allowlist). */
export function allowBrText(input) {
  if (typeof input !== 'string') return ''
  const escaped = input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // Restore line breaks represented as <br> or <br/> in the source
  return escaped
    .replace(/&lt;br\s*\/?&gt;/gi, '<br>')
}
