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
  it('renders links while preserving surrounding text', () => {
    expect(renderInlineMarkdown('Read [the article](https://example.com/article) or [the news](/news/).'))
      .toBe('Read <a href="https://example.com/article">the article</a> or <a href="/news/">the news</a>.')
  })
  it.each([
    ['**Read more**', '<strong>Read more</strong>'],
    ['*Read more*', '<em>Read more</em>'],
    ['***Read more***', '<strong><em>Read more</em></strong>'],
  ])('formats the link label %s', (label, expected) => {
    expect(renderInlineMarkdown(`[${label}](https://example.com/article)`))
      .toBe(`<a href="https://example.com/article">${expected}</a>`)
  })
  it('supports bold surrounding a link', () => {
    expect(renderInlineMarkdown('**Read [the article](https://example.com/article)**'))
      .toBe('<strong>Read <a href="https://example.com/article">the article</a></strong>')
  })
  it('keeps unmatched formatting in a label separate from surrounding text', () => {
    expect(renderInlineMarkdown('[Read *more](/news/) and *other text*'))
      .toBe('<a href="/news/">Read *more</a> and <em>other text</em>')
  })
  it('preserves formatting characters in link destinations', () => {
    expect(renderInlineMarkdown('[Read more](https://example.com/**article**?q=*city*&page=2)'))
      .toBe('<a href="https://example.com/**article**?q=*city*&amp;page=2">Read more</a>')
  })
  it('preserves balanced parentheses in link destinations', () => {
    expect(renderInlineMarkdown('[Read more](https://example.com/award_(city_(2026)))'))
      .toBe('<a href="https://example.com/award_(city_(2026))">Read more</a>')
  })
  it('escapes HTML in link labels', () => {
    expect(renderInlineMarkdown('[**<img src=x onerror=alert(1)> & more**](/news/)'))
      .toBe('<a href="/news/"><strong>&lt;img src=x onerror=alert(1)&gt; &amp; more</strong></a>')
  })
  it('escapes quotes and ampersands in relative link destinations', () => {
    expect(renderInlineMarkdown('[Read more](/news/"onmouseover="alert(1)?a=1&b=2)'))
      .toBe('<a href="/news/&quot;onmouseover=&quot;alert(1)?a=1&amp;b=2">Read more</a>')
  })
  it.each([
    'javascript:alert(1)',
    'JaVaScRiPt:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'jav&#x61;script:alert(1)',
    'not-a-url',
  ])('leaves an unsafe or invalid destination nonclickable: %s', (url) => {
    expect(renderInlineMarkdown(`[**Read more**](${url})`))
      .toBe('<strong>Read more</strong>')
  })
  it.each([
    '[Read more](https://example.com/article',
    '[Read more](https://example.com/award_(2026)',
    '[Read more](https://example.com/with space)',
    '[Read more]()',
  ])('preserves incomplete or malformed link syntax: %s', (text) => {
    expect(renderInlineMarkdown(text)).toBe(text)
  })
  it.each(['', ' ', ' end of paragraph.'])('renders long unfinished links without blocking with suffix %j', (suffix) => {
    const text = '[x]('.repeat(12000) + suffix
    const start = performance.now()
    expect(renderInlineMarkdown(text)).toBe(text)
    expect(performance.now() - start).toBeLessThan(1000)
  })
  it.each(['', ' rest'])('preserves an inner link when the outer destination is unfinished with suffix %j', (suffix) => {
    expect(renderInlineMarkdown('[a](xx[b](/y)' + suffix))
      .toBe('[a](xx<a href="/y">b</a>' + suffix)
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
