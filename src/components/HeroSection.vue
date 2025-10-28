<template>
  <section class="hero gradient-hero" role="region" aria-roledescription="carousel" :aria-label="`Hero slideshow (${slides.length} slides)`">
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
import { ref, computed } from 'vue'
import { allowBrText } from '../utils/sanitize'

const BASE_URL = import.meta.env.BASE_URL || '/'
const slides = [
  {
    id: 0,
    title: 'A smarter city starts<br>with a digital twin.',
    video: `${BASE_URL}ssstik.io_1757779073094.mp4`,
    poster: ''
  },
  {
    id: 1,
    title: 'Plan with confidence.<br>Test before you build.',
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
