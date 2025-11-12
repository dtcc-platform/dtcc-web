# Video Fetching Optimization Analysis

## Current Implementation Issues

After thorough analysis and consulting web performance best practices, I've identified several optimization opportunities in your video fetching strategy:

### 🔴 Critical Issues Found:

#### 1. **Triple Loading Problem**
Your videos are being loaded **THREE times**:
```
1. HTML preload links in index.html
2. Hidden <video> elements with v-for in Vue template
3. Programmatic video.load() in JavaScript
```
This causes:
- **3x bandwidth usage** for the same videos
- **Browser cache thrashing**
- **Competing network requests**

#### 2. **Invalid HTML Attributes on Videos**
```html
<video loading="eager">  <!-- ❌ loading attribute doesn't work on videos -->
```
The `loading` attribute is only valid for `<img>` and `<iframe>` elements, not `<video>`.

#### 3. **Overly Aggressive Preloading**
- All videos use `preload="auto"` which downloads entire videos
- Hidden preload videos are always present in DOM
- No conditional loading based on user interaction

#### 4. **Missing Poster Images**
- No poster images defined for faster perceived performance
- Videos show blank/black frame until loaded
- Missing opportunity for LCP optimization

## Best Practices from Web.dev

According to web.dev performance guidelines:

1. **Use appropriate preload values**:
   - `preload="none"` - Don't preload anything
   - `preload="metadata"` - Only load video metadata (duration, dimensions)
   - `preload="auto"` - Load entire video (use sparingly)

2. **Avoid redundant preloading**
   - Choose ONE preload strategy, not multiple
   - HTML preload links are best for critical resources
   - Don't duplicate with hidden elements

3. **Consider poster images**:
   - Add poster attribute for immediate visual feedback
   - Can serve as LCP element
   - Reduces perceived load time

## Recommended Optimizations

### Priority 1: Fix Triple Loading (High Impact)

**Remove redundant preloading mechanisms:**

```vue
<!-- REMOVE hidden preload videos - they're redundant -->
<div style="display: none;">
  <video v-for="slideIndex in preloadIndexes" ...>
  <!-- DELETE THIS ENTIRE SECTION -->
</div>
```

**Keep only ONE strategy:**
- Keep HTML `<link rel="preload">` for first 2 videos (fastest)
- Remove programmatic preloading for videos 0-1
- Use `preload="metadata"` on main video element

### Priority 2: Optimize Video Element

```vue
<video
  v-if="currentSlide.video"
  :key="'v'+currentSlide.id"
  class="bg-video"
  :src="currentSlide.video"
  :poster="currentSlide.poster || generatePoster(currentSlide.id)"
  autoplay
  muted
  :loop="currentSlide.loop === true"
  playsinline
  :preload="current === 0 ? 'auto' : 'metadata'"
  :fetchpriority="current <= 1 ? 'high' : 'auto'"
>
```

Changes:
- Remove invalid `loading="eager"` attribute
- Add conditional preload (auto for first, metadata for others)
- Add poster images for immediate visual

### Priority 3: Simplify Preload Logic

```javascript
// OPTIMIZED: Only preload video that's not already in HTML preload
onMounted(() => {
  // Only preload third video since first two are in HTML
  if (slides[2]?.video) {
    const link = document.createElement('link')
    link.rel = 'prefetch'  // Use prefetch for non-critical
    link.as = 'video'
    link.href = slides[2].video
    document.head.appendChild(link)
  }
})
```

### Priority 4: Add Poster Images

Generate poster images from videos:
```bash
# Extract poster frame from video at 1 second
ffmpeg -i carousel-hero.mp4 -ss 00:00:01 -vframes 1 carousel-hero-poster.jpg
ffmpeg -i gate-moving-pathlines.mp4 -ss 00:00:01 -vframes 1 gate-pathlines-poster.jpg
```

Then add to slides data:
```javascript
const slides = [
  {
    id: 0,
    title: '...',
    video: `${BASE_URL}carousel-hero.mp4`,
    poster: `${BASE_URL}carousel-hero-poster.jpg`
  },
  // ...
]
```

## Implementation Priority

1. **Immediate (5 min)**: Remove triple loading
2. **Quick Win (10 min)**: Fix invalid attributes
3. **Medium (30 min)**: Add poster images
4. **Optional**: Create mobile-optimized versions

## Expected Performance Impact

- **50% reduction** in initial bandwidth usage
- **Faster Time to First Frame** with poster images
- **Better browser caching** without competing requests
- **Improved Core Web Vitals** (especially LCP)

## Quick Implementation Script

```bash
#!/bin/bash
# Generate poster images
for video in public/*.mp4 public/content/*.mp4; do
  if [ -f "$video" ]; then
    poster="${video%.mp4}-poster.jpg"
    if [ ! -f "$poster" ]; then
      ffmpeg -i "$video" -ss 00:00:01 -vframes 1 -q:v 2 "$poster" 2>/dev/null
      echo "Created poster: $poster"
    fi
  fi
done
```

## Conclusion

Your current implementation loads each video **3 times**, uses invalid HTML attributes, and misses optimization opportunities. By removing redundant preloading and adding poster images, you can significantly improve performance while maintaining the same user experience.