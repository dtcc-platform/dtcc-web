import { escapeHtml, sanitizeUrl } from './sanitize.js'

/**
 * Convert minimal inline markdown (**bold**, *italic*, [text](url)) to HTML.
 *
 * Escape input before formatting and validate link destinations before
 * generating HTML. Only the <strong>, <em>, and <a> tags we produce are allowed.
 */
export function renderInlineMarkdown(text) {
  if (typeof text !== 'string') return ''
  if (!text) return ''

  const links = []
  const linkPattern = /\[([^\[\]\r\n]+)\]\(/g
  let result = ''
  let lastIndex = 0

  // Pair parentheses within each whitespace-free run once, so unfinished
  // destinations do not repeatedly scan the same text for later candidates.
  const openingParentheses = []
  const closingParentheses = new Map()
  for (let i = 0; i < text.length; i++) {
    if (/\s/.test(text[i])) openingParentheses.length = 0
    else if (text[i] === '(') openingParentheses.push(i)
    else if (text[i] === ')' && openingParentheses.length) {
      closingParentheses.set(openingParentheses.pop(), i)
    }
  }

  for (let match; (match = linkPattern.exec(text));) {
    const urlStart = linkPattern.lastIndex
    const closingIndex = closingParentheses.get(urlStart - 1)
    if (closingIndex === undefined || closingIndex === urlStart) continue
    const end = closingIndex + 1

    const label = renderEmphasis(escapeHtml(match[1]))
    const href = sanitizeUrl(text.slice(urlStart, end - 1))
    result += escapeHtml(text.slice(lastIndex, match.index))
    // Input is escaped, so it cannot forge these markers. Keep generated links
    // out of the emphasis pass so URL characters never become formatting.
    result += `<link${links.length}>`
    links.push(href === '#' ? label : `<a href="${escapeHtml(href)}">${label}</a>`)
    lastIndex = end
    linkPattern.lastIndex = end
  }

  result += escapeHtml(text.slice(lastIndex))
  return renderEmphasis(result).replace(/<link(\d+)>/g, (_, index) => links[index])
}

function renderEmphasis(escapedText) {
  let result = escapedText

  // Bold-italic: ***text*** must be handled before ** and * to avoid
  // the bold pass consuming only two of the three leading asterisks.
  result = result.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')

  // Bold: **text** (non-greedy, single-line only)
  result = result.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Italic: *text* -- negative lookbehind/lookahead for * prevents
  // matching inside bold delimiters or consuming *** patterns incorrectly.
  result = result.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')

  return result
}
