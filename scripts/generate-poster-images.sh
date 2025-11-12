#!/bin/bash

# Generate poster images for carousel videos
# This creates static images from video frames for instant display

echo "==================================="
echo "GENERATING POSTER IMAGES FOR VIDEOS"
echo "==================================="
echo

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed. Please install it first:"
    echo "   Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    exit 1
fi

# Configuration
VIDEOS=(
    "public/carousel-hero.mp4"
    "public/content/gate-moving-pathlines.mp4"
)

# Generate poster for each video
for video in "${VIDEOS[@]}"; do
    if [ -f "$video" ]; then
        # Generate poster filename (replace .mp4 with -poster.jpg)
        poster="${video%.mp4}-poster.jpg"

        echo "Processing: $video"

        # Extract frame at 1 second with high quality
        ffmpeg -i "$video" -ss 00:00:01.000 -vframes 1 -q:v 2 "$poster" -y 2>/dev/null

        if [ -f "$poster" ]; then
            size=$(ls -lh "$poster" | awk '{print $5}')
            echo "✅ Created: $poster ($size)"
        else
            echo "❌ Failed to create poster for $video"
        fi
    else
        echo "⚠️  Video not found: $video"
    fi
done

echo
echo "==================================="
echo "✅ POSTER GENERATION COMPLETE"
echo "==================================="
echo
echo "Next steps:"
echo "1. Update your Vue component to include poster images:"
echo
echo "const slides = ["
echo "  {"
echo "    id: 0,"
echo "    title: 'A smarter city starts<br>with a digital twin.',"
echo "    video: \`\${BASE_URL}carousel-hero.mp4\`,"
echo "    poster: \`\${BASE_URL}carousel-hero-poster.jpg\`"
echo "  },"
echo "  {"
echo "    id: 1,"
echo "    title: 'Plan with confidence.<br>Test before you build.',"
echo "    video: \`\${BASE_URL}content/gate-moving-pathlines.mp4\`,"
echo "    poster: \`\${BASE_URL}content/gate-moving-pathlines-poster.jpg\`"
echo "  },"
echo "  // ..."
echo "]"
echo
echo "2. Optionally add preload links for poster images in index.html:"
echo '   <link rel="preload" as="image" href="/carousel-hero-poster.jpg" fetchpriority="high">'