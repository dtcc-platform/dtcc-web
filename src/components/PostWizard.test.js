import { describe, it, expect } from 'vitest'
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'
import PostWizard from './PostWizard.vue'

async function renderPreview(section) {
  const app = createSSRApp({
    ...PostWizard,
    setup(props, context) {
      const state = PostWizard.setup(props, context)
      state.postType.value = section
      state.isPreviewOpen.value = true
      state.previewData.value = {
        section,
        title: 'Preview check',
        intro: '',
        bodyParagraphs: ['See [**the site**](https://example.com/preview-check).'],
        gallery: [],
        contacts: [],
        related: [],
        relatedProjects: [],
        papers: [],
      }
      return state
    },
  })
  return renderToString(app)
}

describe('PostWizard body preview', () => {
  it.each(['projects', 'events', 'events-archive'])('keeps %s text literal like the published page', async (section) => {
    expect(await renderPreview(section))
      .toContain('See [**the site**](https://example.com/preview-check).')
  })

  it('renders bold links for news posts', async () => {
    expect(await renderPreview('news'))
      .toContain('See <a href="https://example.com/preview-check"><strong>the site</strong></a>.')
  })
})
