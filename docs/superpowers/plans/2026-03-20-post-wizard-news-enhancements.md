# Post Wizard News Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the Post Wizard and News detail page with three features: remove "Details" heading, add related projects selector for news, and support bold/italic markdown in body text.

**Architecture:** Each feature is independent and can be implemented in sequence. Feature 3 (markdown) requires a new utility module with a shared `escapeHtml` function extracted from `sanitize.js`. All changes are localized to two Vue components (`NewsDetail.vue`, `PostWizard.vue`) and two utility files (`sanitize.js`, new `markdown.js`).

**Tech Stack:** Vue 3 (Composition API), Vite, Vitest (new dev dependency for testing)

**Spec:** `docs/superpowers/specs/2026-03-20-post-wizard-news-enhancements-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/utils/sanitize.js` | Modify | Extract `escapeHtml` as shared export; `allowBrText` reuses it |
| `src/utils/markdown.js` | Create | `renderInlineMarkdown(text)` -- escapes HTML then converts `**bold**` and `*italic*` |
| `src/utils/markdown.test.js` | Create | Unit tests for `escapeHtml` and `renderInlineMarkdown` |
| `src/components/NewsDetail.vue` | Modify | Remove "Details" heading, add related projects section, use markdown in body |
| `src/components/PostWizard.vue` | Modify | Related projects selector, preview updates, body helper text |
| `package.json` | Modify | Add vitest dev dependency |
| `vite.config.js` | Modify | Add vitest test config |

---

## Task 1: Set up Vitest

No test runner exists in this project. Add vitest so we can TDD the markdown utility.

**Files:**
- Modify: `package.json`
- Modify: `vite.config.js`

- [ ] **Step 1: Install vitest**

```bash
npm install --save-dev vitest
```

- [ ] **Step 2: Add test config to vite.config.js**

Add a `test` block to the existing Vite config:

```js
// Inside defineConfig, add at the top level alongside `plugins`, `build`, etc:
  test: {
    globals: true,
  },
```

- [ ] **Step 3: Add test script to package.json**

Add to the `"scripts"` object:

```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 4: Verify vitest runs**

```bash
npm test
```

Expected: vitest runs and reports "no test files found" (no failures).

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json vite.config.js
git commit -m "chore: add vitest for unit testing"
```

---

## Task 2: Extract `escapeHtml` from `sanitize.js`

Refactor `sanitize.js` to export a standalone `escapeHtml` function. `allowBrText` reuses it.

**Files:**
- Modify: `src/utils/sanitize.js:32-42`
- Create: `src/utils/markdown.test.js` (escapeHtml tests only for now)

- [ ] **Step 1: Write failing tests for escapeHtml**

Create `src/utils/markdown.test.js`:

```js
import { describe, it, expect } from 'vitest'
import { escapeHtml } from '../utils/sanitize.js'

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
```

- [ ] **Step 2: Run tests -- verify they fail**

```bash
npm test
```

Expected: FAIL -- `escapeHtml` is not exported from `sanitize.js`.

- [ ] **Step 3: Extract escapeHtml and update allowBrText**

In `src/utils/sanitize.js`, replace lines 32-42 with:

```js
/** Escape HTML special characters. */
export function escapeHtml(input) {
  if (typeof input !== 'string') return ''
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** Escape all HTML then permit <br> tags back (simple allowlist). */
export function allowBrText(input) {
  if (typeof input !== 'string') return ''
  const escaped = escapeHtml(input)
  return escaped.replace(/&lt;br\s*\/?&gt;/gi, '<br>')
}
```

Note: The original `allowBrText` did not escape `"`. The new `escapeHtml` adds it for completeness (needed by the markdown utility). `allowBrText` behavior is unchanged since `<br>` tags never contain quotes.

- [ ] **Step 4: Run tests -- verify they pass**

```bash
npm test
```

Expected: All `escapeHtml` tests PASS.

- [ ] **Step 5: Add non-regression test for allowBrText**

Add to `src/utils/markdown.test.js`:

```js
import { escapeHtml, allowBrText } from '../utils/sanitize.js'

// ... existing escapeHtml tests ...

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
```

- [ ] **Step 6: Run tests -- verify all pass**

```bash
npm test
```

Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/utils/sanitize.js src/utils/markdown.test.js
git commit -m "refactor: extract escapeHtml from sanitize.js for reuse"
```

---

## Task 3: Implement `renderInlineMarkdown`

Create the markdown utility that converts `**bold**` and `*italic*` with HTML escaping.

**Files:**
- Create: `src/utils/markdown.js`
- Modify: `src/utils/markdown.test.js`

- [ ] **Step 1: Write failing tests for renderInlineMarkdown**

Add to `src/utils/markdown.test.js`:

```js
import { renderInlineMarkdown } from '../utils/markdown.js'

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
```

- [ ] **Step 2: Run tests -- verify they fail**

```bash
npm test
```

Expected: FAIL -- `markdown.js` does not exist yet.

- [ ] **Step 3: Implement renderInlineMarkdown**

Create `src/utils/markdown.js`:

```js
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

  // Bold: **text** (non-greedy, single-line only)
  result = result.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Italic: *text* -- negative lookbehind/lookahead for * prevents
  // matching inside bold delimiters or consuming *** patterns incorrectly.
  result = result.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')

  return result
}
```

- [ ] **Step 4: Run tests -- verify they pass**

```bash
npm test
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/utils/markdown.js src/utils/markdown.test.js
git commit -m "feat: add renderInlineMarkdown utility for bold/italic support"
```

---

## Task 4: Remove "Details" heading from NewsDetail

Remove the "Details" `<h2>` and flatten the body section from a two-column grid to a single container.

**Files:**
- Modify: `src/components/NewsDetail.vue:25-61` (template) and `:219` (data normalization)

- [ ] **Step 1: Remove the heading and flatten the body section template**

In `src/components/NewsDetail.vue`, replace lines 25-61 (the entire body `<section>` including its closing tag) with:

```html
    <!-- Body section -->
    <section class="section gradient-sunrise body">
      <div class="container">
        <p class="brodtext-20 muted" v-for="(p, i) in bodyParas" :key="i" v-text="p" />
        <div v-if="galleryItems.length" class="gallery">
          <figure
            v-for="(image, i) in galleryItems"
            :key="`${i}-${image.src}`"
            class="gallery-card"
          >
            <a :href="image.src" target="_blank" rel="noopener">
              <img
                :src="image.src"
                :alt="image.caption || `${item.title} image ${i + 2}`"
                loading="lazy"
                decoding="async"
              />
            </a>
            <figcaption v-if="image.caption" class="caption">{{ image.caption }}</figcaption>
          </figure>
        </div>
        <div v-if="videoEmbed" class="video-wrap">
          <iframe
            :src="videoEmbed"
            title="YouTube video player"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
            loading="lazy"
          ></iframe>
        </div>
      </div>
    </section>
```

- [ ] **Step 2: Remove dead subheading field from data normalization**

In `src/components/NewsDetail.vue`, line 219, remove the `subheading` property from the `item.value` assignment:

```js
// Remove this line:
      subheading: data.subheading || data.headline || 'Details',
```

- [ ] **Step 3: Verify the build succeeds**

```bash
npm run build
```

Expected: Build succeeds with no errors.

- [ ] **Step 4: Commit**

```bash
git add src/components/NewsDetail.vue
git commit -m "feat: remove Details heading from news detail pages"
```

---

## Task 5: Use `renderInlineMarkdown` in NewsDetail body

Switch body paragraph rendering from `v-text` to `v-html` with markdown support.

**Files:**
- Modify: `src/components/NewsDetail.vue`

- [ ] **Step 1: Import renderInlineMarkdown**

At the top of the `<script setup>` block in `NewsDetail.vue` (after the existing imports around line 110), add:

```js
import { renderInlineMarkdown } from '../utils/markdown.js'
```

- [ ] **Step 2: Switch body paragraphs from v-text to v-html**

In the template, change the body paragraph `<p>` tag from:

```html
        <p class="brodtext-20 muted" v-for="(p, i) in bodyParas" :key="i" v-text="p" />
```

to:

```html
        <p class="brodtext-20 muted" v-for="(p, i) in bodyParas" :key="i" v-html="renderInlineMarkdown(p)" />
```

- [ ] **Step 3: Verify build**

```bash
npm run build
```

Expected: Build succeeds.

- [ ] **Step 4: Commit**

```bash
git add src/components/NewsDetail.vue
git commit -m "feat: render bold/italic markdown in news body paragraphs"
```

---

## Task 6: Add related projects section to NewsDetail

Fetch and render related projects on news detail pages.

**Files:**
- Modify: `src/components/NewsDetail.vue`

- [ ] **Step 1: Add relatedProjects ref and projectDetailHref helper**

In the `<script setup>` block, after the existing `related` ref (around line 125), add:

```js
const relatedProjects = ref([])

const projectDetailHref = (slug) => withBase(`projects/detail.html?slug=${encodeURIComponent(slug)}`)
```

- [ ] **Step 2: Fetch relatedProjects in onMounted**

In the `onMounted` callback, after the existing related news fetch block (around line 251), add the relatedProjects fetch:

```js
    const relatedProjectSlugs = Array.isArray(data.relatedProjects) ? data.relatedProjects.slice(0, 4) : []
    if (relatedProjectSlugs.length) {
      const projectResults = await Promise.all(
        relatedProjectSlugs.map(async (refSlug) => {
          if (!isValidSlug(refSlug)) return null
          try {
            const refRes = await fetch(resolveUrl(`content/projects/${refSlug}.json`), { cache: 'default' })
            if (!refRes.ok) return null
            const refData = await refRes.json()
            return {
              id: refSlug,
              title: refData.title || refSlug,
              summary: refData.summary || refData.excerpt || '',
              image: normalizeImage(refData.image || (Array.isArray(refData.images) ? refData.images[0] : null)),
            }
          } catch (_) {
            return null
          }
        })
      )
      relatedProjects.value = projectResults.filter(Boolean)
    }
```

- [ ] **Step 3: Add v-if to existing Related posts section**

On the existing "Related posts" `<section>` tag (around line 79), add `v-if="related.length"`:

```html
    <section v-if="related.length" class="section gradient-sunrise related">
```

- [ ] **Step 4: Add Related projects template section**

Insert a new section between the "Related posts" section and the "Associated papers" section:

```html
    <!-- Related projects -->
    <section v-if="relatedProjects.length" class="section gradient-sunrise related">
      <div class="container">
        <h3 class="h3-30 section-title">Related projects</h3>
        <div class="cards">
          <article v-for="rp in relatedProjects" :key="rp.id" class="card project">
            <div class="img" :style="{ backgroundImage: rp.image ? `url(${rp.image})` : undefined }"></div>
            <div class="body">
              <h4 class="h3-30" v-text="rp.title" />
              <p class="brodtext-20 muted" v-text="rp.summary || ''" />
              <a :href="projectDetailHref(rp.id)" class="more">Read more &raquo;</a>
            </div>
          </article>
        </div>
      </div>
    </section>
```

- [ ] **Step 5: Verify build**

```bash
npm run build
```

Expected: Build succeeds.

- [ ] **Step 6: Commit**

```bash
git add src/components/NewsDetail.vue
git commit -m "feat: add related projects section to news detail pages"
```

---

## Task 7: Add related projects selector to PostWizard

Add the "Related projects" checkbox selector for news items in the PostWizard form.

**Files:**
- Modify: `src/components/PostWizard.vue`

- [ ] **Step 1: Add state variables**

After the existing related state declarations (around line 713-720), add:

```js
const selectedRelatedProjects = ref([])
const relatedProjectOptions = ref([])
const relatedProjectsLoading = ref(false)
const relatedProjectsError = ref('')
const relatedProjectsSelectionFull = computed(() => selectedRelatedProjects.value.length >= MAX_RELATED)
```

- [ ] **Step 2: Add toggle and check helpers**

After the existing `toggleRelated` / `isRelatedSelected` functions, add:

```js
function isRelatedProjectSelected(slug) {
  return selectedRelatedProjects.value.includes(slug)
}

function toggleRelatedProject(slug, checked) {
  if (checked) {
    if (isRelatedProjectSelected(slug) || selectedRelatedProjects.value.length >= MAX_RELATED) return
    selectedRelatedProjects.value = [...selectedRelatedProjects.value, slug]
  } else {
    selectedRelatedProjects.value = selectedRelatedProjects.value.filter((s) => s !== slug)
  }
}
```

- [ ] **Step 3: Add refresh function for project options**

After the existing `refreshRelatedOptions` function (around line 1548), add:

```js
async function refreshRelatedProjectOptions() {
  relatedProjectsLoading.value = true
  relatedProjectsError.value = ''
  try {
    const manifestUrl = `${basePath}/content/projects/index.json`
    const res = await fetch(manifestUrl, { cache: 'no-store' })
    const manifest = res.ok ? await res.json() : null
    const items = Array.isArray(manifest?.items) ? manifest.items : []
    const options = []

    for (const item of items) {
      const slug = item.base || item.slug
      if (!slug || !isValidSlug(slug)) continue
      try {
        const detailUrl = resolveUrl(`content/projects/${slug}.json`)
        const detailRes = await fetch(detailUrl, { cache: 'no-store' })
        if (!detailRes.ok) continue
        const detail = await detailRes.json()
        options.push({
          slug,
          title: detail.title || detail.name || slug,
        })
      } catch (_) {
        // ignore individual fetch failures
      }
    }

    relatedProjectOptions.value = options
    selectedRelatedProjects.value = selectedRelatedProjects.value.filter((slug) =>
      options.some((option) => option.slug === slug)
    )
  } catch (err) {
    relatedProjectsError.value = err instanceof Error ? err.message : String(err)
    relatedProjectOptions.value = []
  } finally {
    relatedProjectsLoading.value = false
  }
}
```

- [ ] **Step 4: Call refresh on mount and postType change**

In `onMounted` (around line 851), after `await refreshRelatedOptions(postType.value)`, add:

```js
  if (!isEventSection(postType.value)) {
    await refreshRelatedProjectOptions()
  }
```

In the existing `watch` on `postType` at line 838 (the watcher callback parameter is `section`), add after `refreshRelatedOptions(section)`:

```js
  if (section === 'news') {
    refreshRelatedProjectOptions()
  } else {
    relatedProjectOptions.value = []
    selectedRelatedProjects.value = []
  }
```

- [ ] **Step 5: Add template for the selector**

In the template, after the existing "Related news items" selector block (after line 113, before the Contacts selector), add. Note: this only shows when `postType === 'news'`:

```html
        <div v-if="postType === 'news'" class="field selection-field">
          <label>Related projects</label>
          <p class="muted helper">Select up to {{ MAX_RELATED }} related projects to feature alongside this news item.</p>
          <div v-if="relatedProjectsLoading" class="muted helper">Loading project options...</div>
          <div v-else-if="relatedProjectsError" class="alert error">{{ relatedProjectsError }}</div>
          <div v-else class="selection-list">
            <label v-for="option in relatedProjectOptions" :key="option.slug" class="selection-option">
              <input
                type="checkbox"
                :checked="isRelatedProjectSelected(option.slug)"
                :disabled="!isRelatedProjectSelected(option.slug) && relatedProjectsSelectionFull"
                @change="toggleRelatedProject(option.slug, $event.target.checked)"
              >
              <span class="option-text">{{ option.title }}</span>
            </label>
            <p v-if="!relatedProjectOptions.length" class="muted helper">No existing projects available yet.</p>
          </div>
        </div>
```

- [ ] **Step 6: Verify build**

```bash
npm run build
```

Expected: Build succeeds.

- [ ] **Step 7: Commit**

```bash
git add src/components/PostWizard.vue
git commit -m "feat: add related projects selector for news items in PostWizard"
```

---

## Task 8: Wire relatedProjects into PostWizard draft, save, and prefill

Connect the related projects selector to draft generation, save path, and edit prefill.

**Files:**
- Modify: `src/components/PostWizard.vue`

- [ ] **Step 1: Add relatedProjects to draft generation**

In `prepareDraft()`, inside the `if (!isEventSection(section))` block (around lines 1862-1873), after the existing `related` and `contacts` handling, add:

```js
    if (postType.value === 'news' && selectedRelatedProjects.value.length) {
      payload.relatedProjects = [...selectedRelatedProjects.value]
    } else {
      delete payload.relatedProjects
    }
```

- [ ] **Step 2: Add relatedProjects to save path**

In the `publishDraft` function, inside the `if (!isEventSection(postType.value))` block (around lines 2104-2118), add after the `contacts` handling:

```js
    if (postType.value === 'news' && selectedRelatedProjects.value.length) {
      parsed.relatedProjects = [...selectedRelatedProjects.value]
    } else {
      delete parsed.relatedProjects
    }
```

- [ ] **Step 3: Add relatedProjects to prefill**

In `prefillExistingEntry` (around line 887), after `selectedRelated.value = cleanSlugList(data.related, MAX_RELATED)`, add:

```js
    selectedRelatedProjects.value = section === 'news'
      ? cleanSlugList(data.relatedProjects, MAX_RELATED)
      : []
```

- [ ] **Step 4: Reset relatedProjects in resetWizard**

Find the `resetWizard` function and add:

```js
    selectedRelatedProjects.value = []
```

- [ ] **Step 5: Verify build**

```bash
npm run build
```

Expected: Build succeeds.

- [ ] **Step 6: Commit**

```bash
git add src/components/PostWizard.vue
git commit -m "feat: wire relatedProjects into PostWizard draft, save, and prefill"
```

---

## Task 9: Update PostWizard preview for all three features

Update the preview panel: skip "Details" heading for news, render markdown in body, show related projects section.

**Files:**
- Modify: `src/components/PostWizard.vue`

- [ ] **Step 1: Import renderInlineMarkdown**

At the top of the `<script setup>` block (around line 654), add:

```js
import { renderInlineMarkdown } from '../utils/markdown.js'
```

- [ ] **Step 2: Skip subheading in preview for news and apply markdown to body**

Replace the entire body section in the preview template (lines 566-602, from `<section class="section gradient-sunrise body">` through its closing `</section>`) with the following complete block:

```html
                <section class="section gradient-sunrise body">
                  <template v-if="previewData.section === 'news'">
                    <div class="container">
                      <p class="brodtext-20 muted" v-for="(paragraph, i) in previewData.bodyParagraphs" :key="i" v-html="renderInlineMarkdown(paragraph)" />
                      <div v-if="previewData.gallery.length" class="gallery">
                        <figure
                          v-for="(image, i) in previewData.gallery"
                          :key="`${i}-${image.src}`"
                          class="gallery-card"
                        >
                          <a :href="image.src" target="_blank" rel="noopener">
                            <img
                              :src="image.src"
                              :alt="image.caption || `Gallery image ${i + 1}`"
                              loading="lazy"
                              decoding="async"
                            >
                          </a>
                          <figcaption v-if="image.caption" class="caption">{{ image.caption }}</figcaption>
                        </figure>
                      </div>
                      <div v-if="previewData.video" class="video-wrap">
                        <iframe
                          :src="previewData.video"
                          title="YouTube video player"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                          referrerpolicy="strict-origin-when-cross-origin"
                          allowfullscreen
                          loading="lazy"
                        ></iframe>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="container grid2">
                      <div>
                        <h2 class="h3-30">{{ previewData.subheading }}</h2>
                      </div>
                      <div>
                        <p class="brodtext-20 muted" v-for="(paragraph, i) in previewData.bodyParagraphs" :key="i" v-html="renderInlineMarkdown(paragraph)" />
                        <div v-if="previewData.gallery.length" class="gallery">
                          <figure
                            v-for="(image, i) in previewData.gallery"
                            :key="`${i}-${image.src}`"
                            class="gallery-card"
                          >
                            <a :href="image.src" target="_blank" rel="noopener">
                              <img
                                :src="image.src"
                                :alt="image.caption || `Gallery image ${i + 1}`"
                                loading="lazy"
                                decoding="async"
                              >
                            </a>
                            <figcaption v-if="image.caption" class="caption">{{ image.caption }}</figcaption>
                          </figure>
                        </div>
                        <div v-if="previewData.video" class="video-wrap">
                          <iframe
                            :src="previewData.video"
                            title="YouTube video player"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                            referrerpolicy="strict-origin-when-cross-origin"
                            allowfullscreen
                            loading="lazy"
                          ></iframe>
                        </div>
                      </div>
                    </div>
                  </template>
                </section>
```

This is a complete, self-contained replacement. For news: flat `<div class="container">` with no subheading. For other types: existing `grid2` layout preserved with subheading. Both branches apply `renderInlineMarkdown` to body paragraphs and include the gallery/video content.

- [ ] **Step 3: Add related projects to preview data**

In the `openPreview` function (around line 2493-2520), after the existing `related` fetch, add:

```js
    const relatedProjectsList = (section === 'news' && Array.isArray(parsed.relatedProjects))
      ? await loadPreviewRelated('projects', parsed.relatedProjects)
      : []
```

Then in the `previewData.value = { ... }` object (around line 2503), add:

```js
      relatedProjects: relatedProjectsList,
```

Note: `loadPreviewRelated` already accepts a section parameter and uses `fetchContentEntry(targetSection, slug)`. Passing `'projects'` makes it fetch from `content/projects/`.

Actually, looking at the existing code: `loadPreviewRelated` maps section to `targetSection` using `section === 'projects' ? 'projects' : 'news'`. Since we're passing `'projects'` directly, it will correctly resolve to `'projects'`. This works without modification to `loadPreviewRelated`.

- [ ] **Step 4: Add related projects template in preview**

After the existing "Related posts" preview section (around line 632), before the papers section, add:

```html
                <section v-if="previewData.relatedProjects && previewData.relatedProjects.length" class="section gradient-sunrise related">
                  <div class="container">
                    <h3 class="h3-30 section-title">Related projects</h3>
                    <div class="cards">
                      <article v-for="rp in previewData.relatedProjects" :key="rp.id" class="card project">
                        <div class="img" :style="{ backgroundImage: rp.image ? `url(${rp.image})` : undefined }"></div>
                        <div class="body">
                          <h4 class="h3-30">{{ rp.title }}</h4>
                          <p class="brodtext-20 muted">{{ rp.summary }}</p>
                          <span class="more">Read more &raquo;</span>
                        </div>
                      </article>
                    </div>
                  </div>
                </section>
```

- [ ] **Step 5: Add markdown helper text to body textarea**

In the form template, find the body textarea helper text (around line 80-82). Change the placeholder and add a helper:

After the closing `</textarea>` for the body field, add a helper paragraph:

```html
          <p class="muted helper">Use blank lines to separate paragraphs. Use **bold** and *italic* for formatting.</p>
```

If there's already a helper or placeholder mentioning blank lines, merge the text rather than duplicating. The existing placeholder on the textarea reads: `"Write the post body. Use blank lines to separate paragraphs."` -- keep that, and add the helper `<p>` below the textarea.

- [ ] **Step 6: Verify build**

```bash
npm run build
```

Expected: Build succeeds.

- [ ] **Step 7: Commit**

```bash
git add src/components/PostWizard.vue
git commit -m "feat: update PostWizard preview for heading removal, markdown, and related projects"
```

---

## Task 10: Final verification

Run all tests and verify the build.

- [ ] **Step 1: Run all tests**

```bash
npm test
```

Expected: All tests PASS.

- [ ] **Step 2: Run production build**

```bash
npm run build
```

Expected: Build succeeds with no errors or warnings.

- [ ] **Step 3: Smoke test with dev server**

```bash
npm run dev
```

Manually verify:
1. Open `/post/` -- the Post Wizard loads
2. Select "News" type -- "Related news items" AND "Related projects" selectors appear
3. Select "Projects" type -- only "Related projects" (same-type) appears, no cross-type selector
4. The body textarea shows the markdown helper text
5. Create a draft -- preview shows no "Details" heading for news, body text renders markdown

- [ ] **Step 4: Commit any final fixes if needed**
