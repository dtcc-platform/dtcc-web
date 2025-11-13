#!/bin/bash

# More aggressive poster image optimization
echo "==================================="
echo "AGGRESSIVE POSTER IMAGE OPTIMIZATION"
echo "==================================="
echo

if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed."
    exit 1
fi

SOURCE="public/content/gate-moving-pathlines-poster.jpg"
echo "Optimizing: $SOURCE"
echo "Current size: $(ls -lh $SOURCE | awk '{print $5}')"
echo

echo "Creating multiple optimization options..."
echo

# Option 1: Lower quality JPEG (quality 60)
echo "1. Lower quality JPEG (q=60):"
ffmpeg -i $SOURCE -q:v 10 -vf "scale=1280:-1" \
    public/content/poster-opt1-q60.jpg -y 2>/dev/null
echo "   Size: $(ls -lh public/content/poster-opt1-q60.jpg 2>/dev/null | awk '{print $5}')"

# Option 2: Smaller resolution (960px wide)
echo "2. Smaller resolution (960px):"
ffmpeg -i $SOURCE -q:v 5 -vf "scale=960:-1" \
    public/content/poster-opt2-small.jpg -y 2>/dev/null
echo "   Size: $(ls -lh public/content/poster-opt2-small.jpg 2>/dev/null | awk '{print $5}')"

# Option 3: WebP format (better compression)
echo "3. WebP format:"
ffmpeg -i $SOURCE -vf "scale=1280:-1" -quality 80 -f webp \
    public/content/poster-opt3.webp -y 2>/dev/null
echo "   Size: $(ls -lh public/content/poster-opt3.webp 2>/dev/null | awk '{print $5}')"

# Option 4: Heavily compressed small JPEG
echo "4. Heavily compressed (640px, q=15):"
ffmpeg -i $SOURCE -q:v 15 -vf "scale=640:-1" \
    public/content/poster-opt4-tiny.jpg -y 2>/dev/null
echo "   Size: $(ls -lh public/content/poster-opt4-tiny.jpg 2>/dev/null | awk '{print $5}')"

# Option 5: Blurred preview (artistic effect + smaller size)
echo "5. Blurred preview (1280px + blur):"
ffmpeg -i $SOURCE -vf "scale=1280:-1,boxblur=2:1" -q:v 8 \
    public/content/poster-opt5-blur.jpg -y 2>/dev/null
echo "   Size: $(ls -lh public/content/poster-opt5-blur.jpg 2>/dev/null | awk '{print $5}')"

echo
echo "==================================="
echo "RECOMMENDATIONS:"
echo "==================================="
echo
echo "For best balance (under 100KB with decent quality):"
echo "  Option 2 or 4 - Smaller resolution"
echo
echo "For modern browsers (best compression):"
echo "  Option 3 - WebP format"
echo
echo "For artistic effect:"
echo "  Option 5 - Blurred preview"
echo
echo "To use one of these:"
echo "  cp public/content/poster-opt[NUMBER].jpg public/content/gate-moving-pathlines-poster.jpg"
echo
echo "Or for WebP (requires updating Vue component):"
echo "  cp public/content/poster-opt3.webp public/content/gate-moving-pathlines-poster.webp"
echo "  Then update the Vue component to use .webp extension"