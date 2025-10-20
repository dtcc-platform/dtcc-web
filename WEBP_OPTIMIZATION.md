# WebP Image Optimization Guide

## Overview

Your site now uses WebP images with automatic PNG/JPEG fallback, reducing image sizes by ~88.7% (from 41.31 MB to 4.65 MB).

## What Was Done

### 1. Image Optimization Script ✅
- Created `scripts/optimize-images.js` to convert large PNGs to WebP
- Optimized 10 large images (7.2MB → 820KB, 5MB → 518KB, etc.)
- Original files backed up to `public/originals/`

### 2. Utility Functions ✅
Added to `src/utils/paths.js`:
- `toWebP(imagePath)` - Converts image paths to .webp extension
- `getOptimizedImageUrl(imagePath)` - Returns WebP version for PNG/JPEG files
- `supportsWebP()` - Detects browser WebP support

### 3. OptimizedImage Component ✅
Created `src/components/OptimizedImage.vue`:
- Automatically serves WebP with PNG/JPEG fallback using `<picture>` element
- Supports lazy loading, async decoding, and aspect ratio
- Works for both local and external images

### 4. Updated Components ✅
Modified these components to use WebP optimization:

**List/Section Components** (background images):
- `NewsSection.vue`
- `ProjectsSection.vue`
- `NewsList.vue`
- `ProjectsList.vue`

**Detail Components** (hero images with OptimizedImage):
- `NewsDetail.vue` - Uses OptimizedImage for hero
- `ProjectsDetail.vue` - Uses OptimizedImage for hero
- `EventDetail.vue` - Uses OptimizedImage for hero

All components now:
- Prefer WebP format when available
- Automatically convert image paths
- Support both runtime and build-time images
- Hero images use `<picture>` element with WebP + fallback

## How to Use

### For Background Images (Current Approach)
Background images automatically use WebP via the `normalizeImage()` function:

```vue
<div :style="{ backgroundImage: `url(${image})` }"></div>
```

The `image` variable is processed through `getOptimizedImageUrl()` which converts PNG/JPEG paths to WebP.

### For Regular Images & Hero Images ✅
All hero images now use the `OptimizedImage` component for better browser compatibility:

```vue
<template>
  <OptimizedImage
    src="/path/to/image.png"
    alt="Description"
    loading="lazy"
  />
</template>

<script setup>
import OptimizedImage from './components/OptimizedImage.vue'
</script>
```

The component automatically:
- Generates `<source srcset="image.webp" type="image/webp">`
- Falls back to `<img src="image.png">` for unsupported browsers

## Running the Optimization Script

To optimize more images in the future:

```bash
npm run optimize-images
```

The script will:
1. Look for PNG/JPEG files in the public directory
2. Create WebP versions with 85% quality
3. Resize to max 1920px width
4. Backup originals to `public/originals/`
5. Show size savings report

## Results

### Before Optimization
- Start-page.png: 7.22 MB
- News-page.png: 4.97 MB
- **Total: 41.31 MB**

### After Optimization
- Start-page.webp: 820 KB (88.9% reduction)
- News-page.webp: 518 KB (89.8% reduction)
- **Total: 4.65 MB (88.7% reduction)**

## Browser Support

WebP is supported by:
- Chrome 32+
- Firefox 65+
- Edge 18+
- Safari 14+
- Opera 19+

For older browsers, the system automatically falls back to PNG/JPEG.

## Best Practices

1. **Always run the optimization script** after adding new images to `/public`
2. **Use descriptive alt text** for accessibility
3. **Use lazy loading** for images below the fold: `loading="lazy"`
4. **Specify dimensions** when possible for better layout stability
5. **Keep originals backed up** in `/public/originals`

## Troubleshooting

### Image not loading?
- Check that the WebP file exists in the same directory as the original
- Verify the path in browser DevTools Network tab
- Ensure the original PNG/JPEG is also present for fallback

### Need to re-optimize?
```bash
# Delete WebP files
find public -name "*.webp" -delete

# Run optimization again
npm run optimize-images
```

### Want to optimize specific images?
Edit `scripts/optimize-images.js` and modify the `IMAGES_TO_OPTIMIZE` array.

## Next Steps

Consider:
1. Setting up automatic optimization in your CI/CD pipeline
2. Using a CDN with automatic WebP conversion
3. Implementing lazy loading for all images
4. Adding image size limits to prevent large uploads
