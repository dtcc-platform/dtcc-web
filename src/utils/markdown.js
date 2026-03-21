import { escapeHtml } from './sanitize.js'

/**
 * Convert minimal inline markdown (**bold**, *italic*) to HTML.
 *
 * Processing order: escape HTML first, then bold, then italic.
 * This ensures only <strong> and <em> tags we produce appear in the output.
 * IMPORTANT: Never reverse this order -- escaping must precede markdown
 * conversion to prevent HTML injection via v-html.
 */
export function renderInlineMarkdown(text) {
  if (typeof text !== 'string') return ''
  if (!text) return ''

  let result = escapeHtml(text)

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
