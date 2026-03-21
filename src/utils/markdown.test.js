import { describe, it, expect } from 'vitest'
import { escapeHtml, allowBrText } from '../utils/sanitize.js'
import { renderInlineMarkdown } from '../utils/markdown.js'

describe('escapeHtml', () => {
  it('escapes < and >', () => {
    expect(escapeHtml('<div>')).toBe('&lt;div&gt;')
  })
  it('escapes &', () => {
    expect(escapeHtml('R&D')).toBe('R&amp;D')
  })
  it('escapes double quotes', () => {
    expect(escapeHtml('"hello"')).toBe('&quot;hello&quot;')
  })
  it('escapes all special chars together', () => {
    expect(escapeHtml('<a href="x">&</a>')).toBe('&lt;a href=&quot;x&quot;&gt;&amp;&lt;/a&gt;')
  })
  it('returns empty string for empty input', () => {
    expect(escapeHtml('')).toBe('')
  })
  it('returns empty string for non-string input', () => {
    expect(escapeHtml(null)).toBe('')
    expect(escapeHtml(undefined)).toBe('')
    expect(escapeHtml(42)).toBe('')
  })
  it('passes through plain text unchanged', () => {
    expect(escapeHtml('hello world')).toBe('hello world')
  })
})

describe('allowBrText (non-regression)', () => {
  it('preserves <br> tags', () => {
    expect(allowBrText('line1<br>line2')).toBe('line1<br>line2')
  })
  it('preserves <br/> tags', () => {
    expect(allowBrText('line1<br/>line2')).toBe('line1<br>line2')
  })
  it('escapes other HTML', () => {
    expect(allowBrText('<b>bold</b>')).toBe('&lt;b&gt;bold&lt;/b&gt;')
  })
})

describe('renderInlineMarkdown', () => {
  it('converts **bold** to <strong>', () => {
    expect(renderInlineMarkdown('**hello**')).toBe('<strong>hello</strong>')
  })
  it('converts *italic* to <em>', () => {
    expect(renderInlineMarkdown('*hello*')).toBe('<em>hello</em>')
  })
  it('handles bold and italic together', () => {
    expect(renderInlineMarkdown('**bold** and *italic*'))
      .toBe('<strong>bold</strong> and <em>italic</em>')
  })
  it('handles ***bold italic***', () => {
    expect(renderInlineMarkdown('***text***'))
      .toBe('<strong><em>text</em></strong>')
  })
  it('escapes HTML before converting markdown', () => {
    expect(renderInlineMarkdown('<script>alert(1)</script>'))
      .toBe('&lt;script&gt;alert(1)&lt;/script&gt;')
  })
  it('handles entities inside bold', () => {
    expect(renderInlineMarkdown('**R&D**'))
      .toBe('<strong>R&amp;D</strong>')
  })
  it('does not match unmatched asterisks', () => {
    expect(renderInlineMarkdown('*not closed'))
      .toBe('*not closed')
  })
  it('returns empty string for empty input', () => {
    expect(renderInlineMarkdown('')).toBe('')
  })
  it('passes through plain text (escaped)', () => {
    expect(renderInlineMarkdown('hello world'))
      .toBe('hello world')
  })
  it('does not match bold across newlines', () => {
    expect(renderInlineMarkdown('**bold\ntext**'))
      .toBe('**bold\ntext**')
  })
  it('does not match italic across newlines', () => {
    expect(renderInlineMarkdown('*italic\ntext*'))
      .toBe('*italic\ntext*')
  })
  it('handles multiple bold segments', () => {
    expect(renderInlineMarkdown('**a** and **b**'))
      .toBe('<strong>a</strong> and <strong>b</strong>')
  })
  it('returns empty string for non-string input', () => {
    expect(renderInlineMarkdown(null)).toBe('')
    expect(renderInlineMarkdown(undefined)).toBe('')
  })
})
