#!/bin/bash

# Video Optimization Script
# Optimizes videos for web delivery using ffmpeg
# Usage: bash scripts/optimize-videos.sh

echo "==================================="
echo "VIDEO OPTIMIZATION SCRIPT"
echo "==================================="
echo
echo "⚠️  This script requires ffmpeg to be installed."
echo "   Install with: apt-get install ffmpeg (Ubuntu) or brew install ffmpeg (Mac)"
echo

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed. Please install it first."
    exit 1
fi

# Configuration
PUBLIC_DIR="public"
BACKUP_DIR="public/video-originals"
CRF_DESKTOP=25  # Quality for desktop (23-28 recommended)
CRF_MOBILE=28   # Quality for mobile (26-30 recommended)

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📹 Videos to optimize:"
echo "------------------------"

# Function to optimize video
optimize_video() {
    local input_file=$1
    local output_name=$(basename "$input_file" .mp4)
    local output_dir=$(dirname "$input_file")

    echo
    echo "Processing: $input_file"

    # Backup original if not already backed up
    if [ ! -f "$BACKUP_DIR/$(basename $input_file)" ]; then
        cp "$input_file" "$BACKUP_DIR/"
        echo "  ✓ Backed up to $BACKUP_DIR/"
    fi

    # Get video info
    original_size=$(ls -lh "$input_file" | awk '{print $5}')
    echo "  Original size: $original_size"

    # Desktop version (1920x1080 max, CRF 25)
    desktop_output="${output_dir}/${output_name}-desktop.mp4"
    echo "  Creating desktop version..."
    ffmpeg -i "$input_file" \
        -c:v libx264 \
        -crf $CRF_DESKTOP \
        -vf "scale='min(1920,iw)':min'(1080,ih)':force_original_aspect_ratio=decrease" \
        -preset slow \
        -profile:v high \
        -level 4.0 \
        -movflags +faststart \
        -an \
        -y "$desktop_output" 2>/dev/null

    if [ -f "$desktop_output" ]; then
        desktop_size=$(ls -lh "$desktop_output" | awk '{print $5}')
        echo "  ✓ Desktop version: $desktop_size"
    fi

    # Mobile version (1280x720 max, CRF 28)
    mobile_output="${output_dir}/${output_name}-mobile.mp4"
    echo "  Creating mobile version..."
    ffmpeg -i "$input_file" \
        -c:v libx264 \
        -crf $CRF_MOBILE \
        -vf "scale='min(1280,iw)':min'(720,ih)':force_original_aspect_ratio=decrease" \
        -preset slow \
        -profile:v baseline \
        -level 3.1 \
        -movflags +faststart \
        -an \
        -y "$mobile_output" 2>/dev/null

    if [ -f "$mobile_output" ]; then
        mobile_size=$(ls -lh "$mobile_output" | awk '{print $5}')
        echo "  ✓ Mobile version: $mobile_size"
    fi

    # WebM version for modern browsers (optional)
    webm_output="${output_dir}/${output_name}.webm"
    echo "  Creating WebM version..."
    ffmpeg -i "$input_file" \
        -c:v libvpx-vp9 \
        -crf 30 \
        -b:v 0 \
        -vf "scale='min(1920,iw)':min'(1080,ih)':force_original_aspect_ratio=decrease" \
        -an \
        -y "$webm_output" 2>/dev/null

    if [ -f "$webm_output" ]; then
        webm_size=$(ls -lh "$webm_output" | awk '{print $5}')
        echo "  ✓ WebM version: $webm_size"
    fi
}

# Process carousel videos
if [ -f "$PUBLIC_DIR/carousel-hero.mp4" ]; then
    optimize_video "$PUBLIC_DIR/carousel-hero.mp4"
fi

if [ -f "$PUBLIC_DIR/content/gate-moving-pathlines.mp4" ]; then
    echo
    echo "Note: gate-moving-pathlines.mp4 is already optimized (CRF=28)"
    echo "      Skipping to avoid quality loss from re-encoding"
fi

echo
echo "==================================="
echo "✅ OPTIMIZATION COMPLETE"
echo "==================================="
echo
echo "📝 Next steps:"
echo "1. Test the optimized videos in your application"
echo "2. Update Vue components to use responsive video loading:"
echo
echo "   <video>"
echo '     <source media="(max-width: 768px)" :src="videoPath + '-mobile.mp4" type="video/mp4">'
echo '     <source :src="videoPath + '-desktop.mp4" type="video/mp4">'
echo '     <source :src="videoPath + '.webm" type="video/webm">'
echo "   </video>"
echo
echo "3. Original videos are backed up in: $BACKUP_DIR"
echo "4. Consider deleting gate-moving-pathlines-original.mp4 (72MB) if not needed"