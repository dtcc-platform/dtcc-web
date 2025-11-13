# Video Poster Images Guide

## What Are Poster Images?

Poster images are static preview frames displayed before a video loads and plays. They provide immediate visual feedback to users while the video is still loading.

### Benefits:
- **Instant Visual Feedback**: Users see content immediately instead of a black/blank frame
- **Improved Perceived Performance**: The page feels faster even if video loading takes time
- **Better LCP (Largest Contentful Paint)**: Poster images can be the LCP element, improving Core Web Vitals
- **Reduced Layout Shift**: Prevents the video area from appearing empty then suddenly filling

## Current Situation

### Videos That Need Posters:
1. `/public/carousel-hero.mp4` (2.1MB)
2. `/public/content/gate-moving-pathlines.mp4` (18MB)

### Challenge:
- **ffmpeg is not installed** on your system
- We need ffmpeg or similar tools to extract frames from videos

## Implementation Options

### Option 1: Install ffmpeg (Recommended)
```bash
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Then run the script:
bash scripts/generate-poster-images.sh
```

### Option 2: Manual Creation
1. **Using Video Player**:
   - Open video in any player (VLC, QuickTime, etc.)
   - Navigate to a good frame (usually 1-2 seconds in)
   - Take a screenshot
   - Save as: `carousel-hero-poster.jpg` and `gate-moving-pathlines-poster.jpg`

2. **Using Online Tools**:
   - Upload videos to an online frame extractor
   - Extract frame at 1-2 second mark
   - Download and save in `/public/` and `/public/content/`

### Option 3: Use Placeholder Images (Quick Fix)
Create gradient or solid color placeholders that match your brand:
```html
<!-- Create via CSS gradient as data URI -->
<video poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1920 1080'%3E%3Cdefs%3E%3ClinearGradient id='g'%3E%3Cstop offset='0%25' stop-color='%231a1a1a'/%3E%3Cstop offset='100%25' stop-color='%23333'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='1920' height='1080' fill='url(%23g)'/%3E%3C/svg%3E">
```

## Once You Have Poster Images

### 1. Update Vue Component
```javascript
const slides = [
  {
    id: 0,
    title: 'A smarter city starts<br>with a digital twin.',
    video: `${BASE_URL}carousel-hero.mp4`,
    poster: `${BASE_URL}carousel-hero-poster.jpg`  // Add this
  },
  {
    id: 1,
    title: 'Plan with confidence.<br>Test before you build.',
    video: `${BASE_URL}content/gate-moving-pathlines.mp4`,
    poster: `${BASE_URL}content/gate-moving-pathlines-poster.jpg`  // Add this
  },
  // ...
]
```

### 2. Add HTML Preload Links
In `/index.html`:
```html
<!-- Preload poster images with high priority -->
<link rel="preload" as="image" href="/carousel-hero-poster.jpg" fetchpriority="high">
<link rel="preload" as="image" href="/content/gate-moving-pathlines-poster.jpg" fetchpriority="high">
```

### 3. Verify Video Element Uses Posters
The video element already references `poster` attribute:
```html
<video
  :poster="currentSlide.poster || ''"
  ...
>
```

## Expected Performance Impact

### With Poster Images:
- **0-100ms**: Poster image displays (instant)
- **100-500ms**: Video loads in background
- **500ms+**: Video ready to play

### Without Poster Images:
- **0-500ms**: Black/empty frame
- **500ms+**: Video suddenly appears

## Recommended Image Specs

- **Format**: JPEG (smaller file size) or WebP (better compression)
- **Resolution**: Match video resolution or 1920x1080 max
- **Quality**: 80-85% compression for balance of quality and size
- **File Size Target**: < 100KB per poster

## Testing Checklist

Once implemented:
- [ ] Poster images display immediately on page load
- [ ] No black frame before video loads
- [ ] Smooth transition from poster to video
- [ ] Poster images are preloaded in Network tab
- [ ] LCP improved in Lighthouse/PageSpeed Insights

## Next Steps

1. **Choose an option** to create poster images
2. **Place files** in correct directories
3. **I'll update** the Vue component and HTML
4. **Test** the implementation

Would you like to:
- Install ffmpeg and auto-generate posters?
- Create posters manually?
- Use placeholder images for now?