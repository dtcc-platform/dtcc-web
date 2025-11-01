#!/usr/bin/env python3
"""
Download and replace expired LinkedIn CDN image URLs with local copies.
This script processes existing linkedin_posts_complete.json and downloads
any images that are still using LinkedIn CDN URLs.
"""

import requests
import json
from pathlib import Path
import hashlib
import mimetypes
import sys


# Configuration
INPUT_FILE = Path("public/content/social/linkedin_posts_complete.json")
IMAGES_DIR = Path("public/content/social/linkedin-images")

# Ensure images directory exists
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def is_linkedin_url(url):
    """Check if URL is a LinkedIn CDN URL"""
    if not url or not isinstance(url, str):
        return False
    return url.startswith('https://media.licdn.com/')


def download_image(image_url, post_id):
    """Download image from URL and save locally, return local path"""
    if not image_url:
        return None

    try:
        # Create a filename from post_id and URL hash
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        post_slug = post_id.split(':')[-1][:12] if post_id else 'unknown'

        # Check if file already exists
        existing_files = list(IMAGES_DIR.glob(f"{post_slug}-{url_hash}.*"))
        if existing_files:
            filename = existing_files[0].name
            relative_path = f"content/social/linkedin-images/{filename}"
            print(f"  ✓ Already exists: {filename}")
            return relative_path

        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        # Detect extension from content-type
        content_type = response.headers.get('content-type', '')
        ext = mimetypes.guess_extension(content_type) or '.jpg'
        if ext == '.jpe':
            ext = '.jpg'

        # Save to local file
        filename = f"{post_slug}-{url_hash}{ext}"
        filepath = IMAGES_DIR / filename

        with filepath.open('wb') as f:
            f.write(response.content)

        # Return relative path for JSON
        relative_path = f"content/social/linkedin-images/{filename}"
        print(f"  ✓ Downloaded: {filename} ({len(response.content)} bytes)")
        return relative_path

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to download (expired or invalid URL): {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return None


def process_posts():
    """Read JSON, download expired images, update with local paths"""
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found")
        sys.exit(1)

    # Read existing JSON
    with INPUT_FILE.open('r', encoding='utf-8') as f:
        data = json.load(f)

    posts = data.get('posts', [])
    if not posts:
        print("No posts found in JSON")
        return

    print(f"=== Processing {len(posts)} LinkedIn Posts ===\n")

    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    for i, post in enumerate(posts, 1):
        post_id = post.get('post_id', 'unknown')
        media = post.get('media', {})
        image_url = media.get('image_url')

        print(f"Post {i}/{len(posts)}: {post_id}")

        # Skip if no image or already local
        if not image_url:
            print("  ⊝ No image")
            skipped_count += 1
            continue

        if not is_linkedin_url(image_url):
            print(f"  ⊝ Already local: {image_url}")
            skipped_count += 1
            continue

        # Download and update
        local_path = download_image(image_url, post_id)
        if local_path:
            # Update the media object
            media['original_image_url'] = image_url
            media['local_image_path'] = local_path
            media['image_url'] = local_path
            downloaded_count += 1
        else:
            failed_count += 1

        print()

    # Update statistics
    data['posts_with_images'] = sum(1 for p in posts if p.get('media', {}).get('image_url'))
    data['posts_with_local_images'] = sum(
        1 for p in posts
        if p.get('media', {}).get('image_url') and not is_linkedin_url(p['media']['image_url'])
    )

    # Save updated JSON
    with INPUT_FILE.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=" * 50)
    print(f"✓ Updated {INPUT_FILE}")
    print(f"  - Downloaded: {downloaded_count}")
    print(f"  - Skipped: {skipped_count}")
    print(f"  - Failed: {failed_count}")
    print(f"  - Total with local images: {data.get('posts_with_local_images', 0)}")


if __name__ == "__main__":
    process_posts()
