#!/bin/bash

# Video Analysis Script
echo "==================================="
echo "VIDEO OPTIMIZATION ANALYSIS"
echo "==================================="
echo

echo "📹 Current Video Files:"
echo "------------------------"
ls -lh public/*.mp4 public/content/*.mp4 2>/dev/null | grep -E "\.mp4$" | awk '{print $NF, "(" $5 ")"}'
echo

echo "📊 Video Encoding Details:"
echo "------------------------"

for video in public/carousel-hero.mp4 public/content/gate-moving-pathlines.mp4 public/content/gate-moving-pathlines-original.mp4; do
    if [ -f "$video" ]; then
        echo "File: $(basename $video)"
        size=$(ls -lh "$video" | awk '{print $5}')
        echo "Size: $size"

        # Extract CRF value from video metadata
        crf=$(strings "$video" | grep -o "crf=[0-9.]*" | head -1)
        if [ ! -z "$crf" ]; then
            echo "Quality: $crf"
        fi

        # Extract codec info
        codec=$(strings "$video" | grep -o "x264 - core [0-9]*" | head -1)
        if [ ! -z "$codec" ]; then
            echo "Codec: H.264/AVC ($codec)"
        fi
        echo
    fi
done

echo "🎯 OPTIMIZATION RECOMMENDATIONS:"
echo "================================="
echo
echo "✅ ALREADY OPTIMIZED:"
echo "• gate-moving-pathlines.mp4 (18MB, CRF=28)"
echo "  - Already compressed from 72MB original (75% size reduction)"
echo "  - Good balance of quality and file size"
echo
echo "⚠️  COULD BE OPTIMIZED:"
echo "• carousel-hero.mp4 (2.1MB, CRF=20)"
echo "  - High quality setting (CRF=20) for a background video"
echo "  - Could use CRF=23-28 for 30-50% size reduction"
echo "  - Already small (2.1MB), optimization impact would be minimal"
echo
echo "🚀 SUGGESTED OPTIMIZATIONS:"
echo "1. For web delivery, consider:"
echo "   - CRF 23-28 for background videos (good quality/size balance)"
echo "   - Max resolution: 1920x1080 for desktop, 1280x720 for mobile"
echo "   - Use H.264 for compatibility or VP9/AV1 for better compression"
echo
echo "2. Create multiple versions:"
echo "   - High quality (1080p) for desktop"
echo "   - Lower quality (720p) for mobile"
echo "   - Use <video> media queries or JavaScript to serve appropriate version"
echo
echo "3. Additional optimizations:"
echo "   - Remove audio track if not needed (saves ~10% size)"
echo "   - Ensure proper keyframe interval for streaming"
echo "   - Consider shorter loop duration for background videos"
echo
echo "📝 To optimize carousel-hero.mp4 with ffmpeg:"
echo "ffmpeg -i carousel-hero.mp4 -c:v libx264 -crf 25 -preset slow -an carousel-hero-optimized.mp4"
echo
echo "Note: gate-moving-pathlines-original.mp4 (72MB) can be deleted if not needed as backup."