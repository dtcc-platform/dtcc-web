# Post Wizard News Enhancements

**Date:** 2026-03-20
**Scope:** Three enhancements to the Post Wizard and News detail page

## Overview

Three targeted improvements to the News post type in the Post Wizard and corresponding News detail rendering:

1. Remove the "Details" heading from news detail pages
2. Add a "Related projects" selector for news items
3. Support bold/italic markdown formatting in the body field

## Feature 1: Remove "Details" heading

### Problem

When viewing a news detail page, a heading reading "Details" appears to the left of the body text. This heading adds no value and clutters the layout.

### Solution

Remove the `<h2>` element and its wrapping `<div>` from the body section in `NewsDetail.vue`. The current body section uses a `grid2` two-column layout where the left column holds only the heading and the right column holds body paragraphs, gallery, and video. The target structure:

- Remove the outer `<div class="container grid2">` and both child `<div>` wrappers.
- Replace with `<div class="container">` containing the body content directly (paragraphs, gallery, video).
- Stop populating `item.subheading` in the data normalization for news (dead code removal).

### PostWizard preview interaction

The preview panel in PostWizard also renders a subheading for the body section. When `postType === 'news'`, the preview should skip the subheading `<h2>` and use a single-column body layout, matching the NewsDetail change.

### Files changed

- `src/components/NewsDetail.vue` -- remove heading element, flatten body section from `grid2` to single `<div class="container">`
- `src/components/PostWizard.vue` -- preview panel: skip subheading and simplify body layout when `postType === 'news'`

### Notes

- The `subheading` field remains in the JSON schema; other post types (projects, events) still use it.

## Feature 2: Related projects on News items

### Problem

The Post Wizard's "Related" selector only shows items of the same type. For news items, editors can link to other news items but not to projects. Editors want to cross-reference relevant projects from news articles.

### Solution

Add a separate `relatedProjects` field to the news JSON schema and a corresponding selector in the Post Wizard.

### JSON schema change

News JSON files gain an optional field:

```json
{
  "relatedProjects": ["urban-trees", "city-model"]
}
```

This is an array of project slugs (filenames without `.json` from `content/projects/`). The existing `related` field continues to hold related news slugs.

Existing news JSON files without `relatedProjects` are unaffected -- the code treats `undefined`/missing as an empty array.

### PostWizard changes

- When `postType === 'news'`, render a second checkbox selector labeled "Related projects" below the existing "Related news items" selector.
- The new selector loads options from `content/projects/index.json`, fetching each project's JSON for the title (same pattern as the existing related loader).
- New state variables: `selectedRelatedProjects`, `relatedProjectOptions`, `relatedProjectsLoading`, `relatedProjectsError`.
- Reuse the existing `MAX_RELATED` constant (4) for consistency with the related news selector.
- On draft generation, write the `relatedProjects` array into the JSON output.
- On the save path (the `if (!isEventSection(...))` block that writes `parsed.related` and `parsed.contacts`), also write or delete `parsed.relatedProjects`.
- On prefill (edit mode), populate `selectedRelatedProjects` from the existing JSON's `relatedProjects` field using `cleanSlugList(data.relatedProjects, MAX_RELATED)`, matching the validation pattern used for `data.related`.

### NewsDetail changes

- On mount, if `data.relatedProjects` exists, validate slugs with `isValidSlug()` and fetch each project's JSON from `content/projects/` in parallel (using `Promise.all`, same as the existing related news fetch). Note: the existing related-news fetch does not validate slugs with `isValidSlug()`; the new `relatedProjects` fetch should apply it regardless. Hardening the existing related-news fetch is out of scope for this change.
- Store in a new `relatedProjects` ref.
- Render a "Related projects" section with `v-if="relatedProjects.length"` (conditional rendering to avoid showing an empty section).
- Cards link to `/projects/detail.html?slug=...` using a new `projectDetailHref` helper (the existing `detailHref` hardcodes the news path).
- Section ordering: related posts, then related projects, then papers.
- Also add `v-if="related.length"` to the existing "Related posts" section for consistency (currently always rendered even when empty).

### PostWizard preview

The preview panel should render a second "Related projects" section for news items. Add a `loadPreviewRelatedProjects` function (mirroring `loadPreviewRelated`) that fetches from `content/projects/` and populates `previewData.relatedProjects`. The preview template renders this section with `v-if` when present and non-empty.

### Files changed

- `src/components/PostWizard.vue` -- new selector, state, fetch logic, draft output, save path, prefill, preview
- `src/components/NewsDetail.vue` -- fetch and render related projects section, conditional rendering on both related sections

## Feature 3: Markdown bold/italic in body

### Problem

The body field is a plain textarea rendered with `v-text`, which escapes all HTML. Editors want to format sub-headlines as bold and use italic for emphasis.

### Solution

A minimal inline markdown parser that converts `**text**` to `<strong>` and `*text*` to `<em>`, with HTML escaping to prevent injection.

### New file: `src/utils/markdown.js`

Exports a single function `renderInlineMarkdown(text)` that:

1. Escapes raw HTML entities (`<`, `>`, `&`, `"`) in the input string using a shared `escapeHtml` helper extracted from `sanitize.js`.
2. Converts `**text**` patterns to `<strong>text</strong>` using `/\*\*(.+?)\*\*/g`.
3. Converts `*text*` patterns to `<em>text</em>` using a regex that requires the `*` not be adjacent to another `*`: `/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g`.
4. Returns the resulting HTML string.

**Processing order matters**: escape first, then bold, then italic. This ensures:
- Only our produced `<strong>` and `<em>` tags appear in the output (security).
- Bold is matched before italic, so `**bold**` is not partially consumed by the italic regex.
- The italic regex uses negative lookahead/lookbehind for `*` to avoid matching inside bold delimiters.

**Entity interaction note**: After HTML escaping, `&` becomes `&amp;`. A string like `**R&D**` becomes `**R&amp;D**` after escaping, which the bold regex correctly wraps as `<strong>R&amp;D</strong>`. The escape step must always precede markdown conversion -- reversing this order would be a security vulnerability. This is documented in code comments.

**Cross-line behavior**: Markdown spans do not cross newline boundaries within a paragraph. The regex patterns use `.` (which does not match `\n` by default), so `**bold\ntext**` will not be matched. This is intentional -- single newlines within a paragraph are preserved as-is.

### Shared `escapeHtml` utility

Extract the HTML escape logic from `sanitize.js`'s `allowBrText` function into a standalone `escapeHtml(input)` export. Both `allowBrText` and `renderInlineMarkdown` use `escapeHtml` as their first step, preventing duplication and divergence. `allowBrText` continues to restore `<br>` tags after escaping. `renderInlineMarkdown` converts markdown syntax after escaping. They are not applied to the same string.

### NewsDetail changes

- Import `renderInlineMarkdown` from `../utils/markdown.js`.
- Body paragraph rendering switches from `v-text="p"` to `v-html="renderInlineMarkdown(p)"`.
- Only the body paragraphs use this; abstract/intro remains `v-text`.

### PostWizard changes

- Add helper text below the body textarea: `Use **bold** and *italic* for formatting`.
- The preview panel body paragraphs switch from `{{ paragraph }}` (text interpolation) to `v-html="renderInlineMarkdown(paragraph)"`.

### Files changed

- `src/utils/sanitize.js` -- extract `escapeHtml` as a shared export; `allowBrText` reuses it
- `src/utils/markdown.js` -- new file, imports `escapeHtml` from sanitize.js
- `src/components/NewsDetail.vue` -- import and use `renderInlineMarkdown` for body paragraphs
- `src/components/PostWizard.vue` -- helper text on body textarea, preview uses `renderInlineMarkdown`

## Security considerations

- **Markdown rendering**: HTML is escaped before markdown conversion, so `v-html` only contains `<strong>` and `<em>` tags produced by our code. No user-supplied HTML passes through. The escape-then-transform order is critical and documented in code.
- **Related projects**: Project slugs are validated with the existing `isValidSlug()` function before use in fetch URLs, preventing path traversal. Prefill uses `cleanSlugList` for the same validation.

## Testing

### `src/utils/markdown.js` tests

The `renderInlineMarkdown` function is a pure utility with clear contracts. Test cases:

- Basic bold: `**hello**` -> `<strong>hello</strong>`
- Basic italic: `*hello*` -> `<em>hello</em>`
- Mixed: `**bold** and *italic*` -> `<strong>bold</strong> and <em>italic</em>`
- Nested: `**bold *and italic***` -- bold wraps the whole phrase; inner `*` are literal
- HTML escaping: `<script>alert(1)</script>` -> escaped, no tags pass through
- Entity interaction: `**R&D**` -> `<strong>R&amp;D</strong>`
- Unmatched asterisks: `*not closed` -> unchanged (no `<em>`)
- Empty string -> empty string
- No markdown -> plain escaped text
- Cross-line: `**bold\ntext**` -> not matched (no `<strong>`)
- Triple asterisks: `***text***` -> `<strong><em>text</em></strong>` (bold regex matches first producing `<strong>*text*</strong>`, then italic converts the inner `*text*`)

### `escapeHtml` tests

- Verify `<`, `>`, `&`, `"` are all escaped
- Verify `allowBrText` still works after refactor (non-regression)

## Out of scope

- Markdown in abstract/intro fields (body only for now)
- Full markdown support (headers, links, lists, code blocks)
- WYSIWYG/rich text editor
- Related projects for post types other than news
- Optimizing the sequential fetch pattern in PostWizard's related options loader (existing behavior, not introduced by this change)
