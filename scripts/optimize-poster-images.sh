#!/bin/bash

# Optimize poster images for web delivery
echo "==================================="
echo "OPTIMIZING POSTER IMAGES"
echo "==================================="
echo

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed. Please install it first."
    exit 1
fi

echo "Current poster image sizes:"
ls -lh public/carousel-hero-poster.jpg public/content/gate-moving-pathlines-poster.jpg

echo
echo "Optimizing gate-moving-pathlines-poster.jpg (currently 600KB)..."

# Optimize the large poster image
# Reduce quality to 85% and resize if needed
ffmpeg -i public/content/gate-moving-pathlines-poster.jpg \
    -q:v 3 \
    -vf "scale='min(1920,iw)':min'(1080,ih)':force_original_aspect_ratio=decrease" \
    public/content/gate-moving-pathlines-poster-optimized.jpg -y 2>/dev/null

if [ -f "public/content/gate-moving-pathlines-poster-optimized.jpg" ]; then
    original_size=$(ls -lh public/content/gate-moving-pathlines-poster.jpg | awk '{print $5}')
    new_size=$(ls -lh public/content/gate-moving-pathlines-poster-optimized.jpg | awk '{print $5}')

    echo "✅ Optimization complete!"
    echo "   Original: $original_size"
    echo "   Optimized: $new_size"
    echo
    echo "To use the optimized version:"
    echo "mv public/content/gate-moving-pathlines-poster-optimized.jpg public/content/gate-moving-pathlines-poster.jpg"
else
    echo "❌ Optimization failed"
fi

echo
echo "Note: The first poster (40KB) is already well-optimized."