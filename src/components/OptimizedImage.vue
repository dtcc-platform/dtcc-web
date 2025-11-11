<template>
  <picture v-if="src" :class="pictureClass">
    <source v-if="webpSrc" :srcset="webpSrc" type="image/webp">
    <img
      :src="src"
      :alt="alt"
      :class="imgClass"
      :loading="loading"
      :decoding="decoding"
      :width="width"
      :height="height"
      v-bind="$attrs"
    >
  </picture>
</template>

<script setup>
import { computed } from 'vue'
import { toWebP } from '../utils/paths'

/**
 * OptimizedImage component
 *
 * Automatically serves WebP images with PNG/JPG fallback using the <picture> element.
 * This provides better performance while maintaining compatibility.
 *
 * Usage:
 * <OptimizedImage src="/path/to/image.png" alt="Description" />
 *
 * The component will automatically:
 * - Serve image.webp to browsers that support it
 * - Fall back to image.png for browsers that don't
 */

const props = defineProps({
  /** Image source path */
  src: {
    type: String,
    required: true
  },
  /** Alt text for accessibility */
  alt: {
    type: String,
    default: ''
  },
  /** CSS class for the picture element */
  pictureClass: {
    type: String,
    default: ''
  },
  /** CSS class for the img element */
  imgClass: {
    type: String,
    default: ''
  },
  /** Loading strategy: 'lazy' or 'eager' */
  loading: {
    type: String,
    default: 'lazy',
    validator: (value) => ['lazy', 'eager'].includes(value)
  },
  /** Decoding hint: 'async', 'sync', or 'auto' */
  decoding: {
    type: String,
    default: 'async',
    validator: (value) => ['async', 'sync', 'auto'].includes(value)
  },
  /** Image width (for aspect ratio) */
  width: {
    type: [String, Number],
    default: undefined
  },
  /** Image height (for aspect ratio) */
  height: {
    type: [String, Number],
    default: undefined
  }
})

// Generate WebP source if the image is a PNG or JPEG
const webpSrc = computed(() => {
  if (!props.src) return null

  // Only generate WebP for local PNG/JPEG files
  const isPngOrJpeg = /\.(png|jpe?g)$/i.test(props.src)
  const isExternal = /^https?:\/\//i.test(props.src) || props.src.startsWith('//')

  if (isPngOrJpeg && !isExternal) {
    return toWebP(props.src)
  }

  return null
})
</script>

<style scoped>
/* Picture element acts as a block container for proper image constraints */
picture {
  display: block;
  line-height: 0; /* Remove any line-height spacing */
}
</style>
