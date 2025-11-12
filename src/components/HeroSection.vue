<template>
  <section
    class="hero gradient-hero"
    role="region"
    aria-roledescription="carousel"
    :aria-label="`Hero slideshow (${slides.length} slides)`"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @mouseleave="handleMouseLeave"
  >
    <!-- Background media (video or image) -->
    <div class="media">
      <transition name="fade" mode="out-in">
        <video
          v-if="currentSlide.video"
          :key="'v'+currentSlide.id"
          class="bg-video"
          :src="currentSlide.video"
          :poster="currentSlide.poster || ''"
          autoplay
          muted
          :loop="currentSlide.loop === true"
          playsinline
          preload="auto"
        ></video>
        <img
          v-else-if="currentSlide.image"
          :key="'i'+currentSlide.id"
          class="bg-image"
          :src="currentSlide.image"
          alt=""
        />
        <div v-else :key="'c'+currentSlide.id" class="bg-fallback" />
      </transition>
      <div class="media-overlay"></div>
    </div>
    <!-- Hidden video elements for preloading adjacent slides -->
    <div style="display: none;">
      <video
        v-for="slideIndex in preloadIndexes"
        :key="'preload-' + slideIndex"
        :src="slides[slideIndex].video"
        preload="auto"
        muted
      />
    </div>
    <div class="hero-stars">
      <div v-for="n in 60" :key="n" class="star" :style="starStyle(n)"></div>
    </div>
    <div class="container hero-inner">
      <transition name="fade" mode="out-in">
        <h1 class="h1-80 title" :key="slides[current].id" v-html="safeTitle"></h1>
      </transition>
      <div class="dots" aria-label="carousel navigation">
        <button
          v-for="(s, i) in slides"
          :key="s.id"
          class="dot"
          :class="{ active: i === current }"
          :aria-label="`Go to slide ${i + 1}`"
          :aria-current="i === current ? 'true' : 'false'"
          @click="go(i)"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { allowBrText } from '../utils/sanitize'

const BASE_URL = import.meta.env.BASE_URL || '/'
const slides = [
  {
    id: 0,
    title: 'A smarter city starts<br>with a digital twin.',
    video: `${BASE_URL}carousel-hero.mp4`,
    poster: ''
  },
  {
    id: 1,
    title: 'Plan with confidence.<br>Test before you build.',
    video: `${BASE_URL}content/gate-moving-pathlines.mp4`,
  },
  {
    id: 2,
    title: 'From data to decisions —<br>creating liveable cities.',
  },
  {
    id: 3,
    title: 'Shaping tomorrow\'s cities<br>with digital twins'
  },
  {
    id: 4,
    title: 'From cutting-edge research<br>to real-world solutions'
  }
]

const current = ref(0)
const currentSlide = computed(() => slides[current.value])
function go(i) { current.value = i }

// Compute which videos to preload (adjacent slides)
const preloadIndexes = computed(() => {
  const indexes = []
  const slidesLength = slides.length

  // Get next slide index
  const nextIndex = (current.value + 1) % slidesLength
  if (slides[nextIndex].video) {
    indexes.push(nextIndex)
  }

  // Get previous slide index
  const prevIndex = (current.value - 1 + slidesLength) % slidesLength
  if (slides[prevIndex].video) {
    indexes.push(prevIndex)
  }

  return indexes
})

// Navigation functions
function nextSlide() {
  current.value = (current.value + 1) % slides.length
}

function prevSlide() {
  current.value = (current.value - 1 + slides.length) % slides.length
}

// Touch tracking for swipe gestures
const touchStartX = ref(0)
const touchStartY = ref(0)
const touchEndX = ref(0)
const touchEndY = ref(0)
const minSwipeDistance = 50 // minimum distance in pixels to trigger swipe

function handleTouchStart(e) {
  touchStartX.value = e.touches[0].clientX
  touchStartY.value = e.touches[0].clientY
}

function handleTouchMove(e) {
  touchEndX.value = e.touches[0].clientX
  touchEndY.value = e.touches[0].clientY
}

function handleTouchEnd() {
  const deltaX = touchEndX.value - touchStartX.value
  const deltaY = Math.abs(touchEndY.value - touchStartY.value)

  // Only trigger swipe if horizontal movement is significant
  // and greater than vertical movement (to avoid interfering with scroll)
  if (Math.abs(deltaX) > minSwipeDistance && Math.abs(deltaX) > deltaY) {
    if (deltaX > 0) {
      // Swiped right - go to previous slide
      prevSlide()
    } else {
      // Swiped left - go to next slide
      nextSlide()
    }
  }

  // Reset tracking
  touchStartX.value = 0
  touchStartY.value = 0
  touchEndX.value = 0
  touchEndY.value = 0
}

// Mouse drag tracking for desktop
const mouseStartX = ref(0)
const mouseStartY = ref(0)
const mouseEndX = ref(0)
const mouseEndY = ref(0)
const isDragging = ref(false)

function handleMouseDown(e) {
  isDragging.value = true
  mouseStartX.value = e.clientX
  mouseStartY.value = e.clientY
}

function handleMouseMove(e) {
  if (isDragging.value) {
    mouseEndX.value = e.clientX
    mouseEndY.value = e.clientY
  }
}

function handleMouseUp() {
  if (!isDragging.value) return

  const deltaX = mouseEndX.value - mouseStartX.value
  const deltaY = Math.abs(mouseEndY.value - mouseStartY.value)

  // Only trigger swipe if horizontal movement is significant
  if (Math.abs(deltaX) > minSwipeDistance && Math.abs(deltaX) > deltaY) {
    if (deltaX > 0) {
      // Dragged right - go to previous slide
      prevSlide()
    } else {
      // Dragged left - go to next slide
      nextSlide()
    }
  }

  // Reset tracking
  isDragging.value = false
  mouseStartX.value = 0
  mouseStartY.value = 0
  mouseEndX.value = 0
  mouseEndY.value = 0
}

function handleMouseLeave() {
  // Reset if mouse leaves the carousel area while dragging
  isDragging.value = false
  mouseStartX.value = 0
  mouseStartY.value = 0
  mouseEndX.value = 0
  mouseEndY.value = 0
}

// Keyboard navigation
function handleKeydown(e) {
  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    prevSlide()
  } else if (e.key === 'ArrowRight') {
    e.preventDefault()
    nextSlide()
  }
}

// Preload all videos on mount for optimal performance
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)

  // Preload all videos by creating video elements
  slides.forEach((slide, index) => {
    if (slide.video && index !== current.value) {
      const video = document.createElement('video')
      video.src = slide.video
      video.preload = 'auto'
      video.muted = true
      video.load() // Explicitly start loading
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// Sanitize slide titles; allow only <br>
const safeTitle = computed(() => allowBrText(String(currentSlide.value?.title || '')))

// Decorative star field helpers
function rand(seed) {
  return (Math.sin(seed * 999) * 10000) % 1
}
function starStyle(n) {
  const t = rand(n)
  const l = rand(n + 1)
  const size = 1 + Math.round(rand(n + 2) * 3)
  const delay = rand(n + 3)
  return {
    left: `${Math.floor(l * 100)}%`,
    top: `${Math.floor(t * 100)}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay * 5}s`
  }
}
</script>

<style scoped>
.hero { position: relative; color: white; padding: 128px 0 96px; overflow: hidden; }
.media { position: absolute; inset: 0; z-index: 0; }
.bg-video, .bg-image, .bg-fallback { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.bg-fallback { background: radial-gradient(60% 40% at 50% 30%, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 60%), linear-gradient(180deg, #101016 0%, #1b1b22 100%); }
.media-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.5) 80%); }
.hero-inner { position: relative; z-index: 1; text-align: center; }
.title { margin: 80px auto 32px; max-width: 900px; }
.dots { display: flex; gap: 8px; justify-content: center; }
.dot { width: 10px; height: 10px; border: 0; padding: 0; border-radius: 50%; background: rgba(255,255,255,0.35); cursor: pointer; }
.dot.active { background: white; }
.star { animation: twinkle 6s infinite ease-in-out; }
.fade-enter-active, .fade-leave-active { transition: opacity .6s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@keyframes twinkle { from { opacity: .2; } 50% { opacity: .9; } to { opacity: .2; } }
@media (max-width: 900px) { .hero { padding: 96px 0 72px; } .title { margin-top: 40px; } }
</style>
