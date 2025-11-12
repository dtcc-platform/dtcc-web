<template>
  <section class="feature">
    <div class="gradient-sunrise angled">
      <div class="container inner">
        <div class="left">
          <h2 class="h2-50">Creating<br>liveable<br>cities.</h2>
        </div>
        <div class="right">
          <div class="video-container">
            <video
              ref="video"
              class="video-player"
              :src="`${BASE_URL}content/dtcc-film.mp4`"
              muted
              loop
              playsinline
              preload="auto"
            ></video>
            <button class="play-btn" @click="togglePlay" :aria-label="isPlaying ? 'Pause video' : 'Play video'">
              {{ isPlaying ? '⏸' : '▶' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const BASE_URL = import.meta.env.BASE_URL || '/'

// Video controls
const video = ref(null)
const isPlaying = ref(false)

const togglePlay = () => {
  if (!video.value) return

  if (video.value.paused) {
    video.value.play()
    isPlaying.value = true
  } else {
    video.value.pause()
    isPlaying.value = false
  }
}
</script>

<style scoped>
.feature { margin: 40px 0; }
.angled { transform: skewY(-3deg); padding: 48px 0; }
.inner { transform: skewY(3deg); display: grid; grid-template-columns: .9fr 1.1fr; gap: 24px; align-items: center; }
.left { padding: 48px 0; }
.video-container {
  position: relative;
  height: 340px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow-card);
}
.video-player {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: saturate(110%);
}
.play-btn {
  position: absolute;
  inset: auto auto 16px 16px;
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  background: rgba(255,255,255,0.9);
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s;
}
.play-btn:hover {
  background: rgba(255,255,255,1);
}
@media (max-width: 900px) {
  .inner { grid-template-columns: 1fr; }
  .video-container { height: 220px; }
}
</style>

