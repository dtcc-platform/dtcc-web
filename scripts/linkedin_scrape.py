import requests
import json
from urllib.parse import quote
import os
from pathlib import Path


# Configuration
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
ORGANIZATION_ID = "100491988"
POSTS_API_BASE = "https://api.linkedin.com/rest/posts"
OUTPUT_FILE = Path("public/content/social/linkedin_posts_complete.json")

def get_post_url(post_id):
    """Convert post ID/URN to a shareable LinkedIn URL"""
    return f"https://www.linkedin.com/feed/update/{post_id}/"

def get_image_details(image_urn, access_token):
    """Fetch image details including download URL from Images API"""
    encoded_urn = quote(image_urn, safe='')
    
    url = f"https://api.linkedin.com/rest/images/{encoded_urn}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202509"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching image {image_urn}: {e}")
        return None

def extract_media_info(post, access_token):
    """Extract media information from a post and fetch image URLs"""
    media_info = {
        "has_media": False,
        "media_type": None,
        "media_urn": None,
        "image_url": None,
        "thumbnail_urn": None,
        "source": "self",
    }
    
    content = post.get('content', {})
    
    # Check for media (image, video, document)
    if 'media' in content:
        media = content['media']
        media_urn = media.get('id', '')
        media_info["media_urn"] = media_urn
        media_info["has_media"] = True
        
        # Determine media type from URN
        if 'image' in media_urn:
            media_info["media_type"] = "image"
            # Fetch image URL
            image_details = get_image_details(media_urn, access_token)
            if image_details:
                media_info["image_url"] = image_details.get('downloadUrl')
        elif 'video' in media_urn:
            media_info["media_type"] = "video"
        elif 'document' in media_urn:
            media_info["media_type"] = "document"
    
    # Check for article with thumbnail
    if 'article' in content:
        article = content['article']
        thumbnail_urn = article.get('thumbnail')
        if thumbnail_urn:
            media_info["has_media"] = True
            media_info["media_type"] = "article_thumbnail"
            media_info["thumbnail_urn"] = thumbnail_urn
            # Fetch thumbnail URL
            image_details = get_image_details(thumbnail_urn, access_token)
            if image_details:
                media_info["image_url"] = image_details.get('downloadUrl')
    
    return media_info


def fetch_post_details(post_urn, access_token, cache):
    """Fetch and cache post details (used for reshare parents)"""
    if not post_urn:
        return None
    if post_urn in cache:
        return cache[post_urn]

    encoded_urn = quote(post_urn, safe='')
    url = f"{POSTS_API_BASE}/{encoded_urn}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202509"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        cache[post_urn] = data
        return data
    except Exception as e:
        print(f"Error fetching parent post {post_urn}: {e}")
        return None

# Fetch posts
url = "https://api.linkedin.com/rest/posts"
params = {
    "author": f"urn:li:organization:{ORGANIZATION_ID}",
    "q": "author",
    "count": 10,
    "sortBy": "LAST_MODIFIED"
}

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": "202509"
}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    print("=== Processing Organization Posts ===\n")
    
    # Enhanced posts data with image URLs and shareable links
    enhanced_posts = []
    post_cache = {}
    
    for i, post in enumerate(data.get('elements', []), 1):
        post_id = post.get('id')
        post_url = get_post_url(post_id)
        commentary = post.get('commentary', 'No text')
        published_at = post.get('publishedAt')
        
        print(f"Processing Post {i}/{len(data.get('elements', []))}...")
        
        # Extract media info
        media_info = extract_media_info(post, ACCESS_TOKEN)

        reshare_context = post.get('reshareContext')
        if (not media_info["has_media"]) and reshare_context:
            parent_urn = reshare_context.get('parent') or reshare_context.get('root')
            parent_post = fetch_post_details(parent_urn, ACCESS_TOKEN, post_cache)
            if parent_post:
                parent_media = extract_media_info(parent_post, ACCESS_TOKEN)
                if parent_media["has_media"]:
                    parent_media["source"] = "reshare_parent"
                    media_info = parent_media
        
        # Create enhanced post object
        enhanced_post = {
            "post_id": post_id,
            "post_url": post_url,
            "published_at": published_at,
            "commentary": commentary,
            "lifecycle_state": post.get('lifecycleState'),
            "visibility": post.get('visibility'),
            "media": media_info,
            "original_data": post  # Keep original post data
        }

        if reshare_context:
            enhanced_post["reshare_parent_id"] = reshare_context.get('parent')
            enhanced_post["reshare_root_id"] = reshare_context.get('root')
            if media_info.get("source") == "reshare_parent":
                enhanced_post["resolved_media_parent_id"] = parent_urn
        
        enhanced_posts.append(enhanced_post)
        
        # Print summary
        print(f"  ✓ ID: {post_id}")
        print(f"  ✓ URL: {post_url}")
        if media_info["has_media"]:
            print(f"  ✓ Media Type: {media_info['media_type']}")
            if media_info["image_url"]:
                print(f"  ✓ Image URL: {media_info['image_url'][:60]}...")
            if media_info.get("source") == "reshare_parent":
                print("  ✓ Media sourced from parent reshare")
        print()
    
    # Save enhanced data to JSON
    output_data = {
        "organization_id": ORGANIZATION_ID,
        "total_posts": len(enhanced_posts),
        "posts_with_media": sum(1 for p in enhanced_posts if p['media']['has_media']),
        "posts_with_images": sum(1 for p in enhanced_posts if p['media']['image_url']),
        "posts": enhanced_posts
    }
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open('w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("=" * 50)
    print(f"✓ Saved {len(enhanced_posts)} posts to {OUTPUT_FILE}")
    print(f"  - Posts with media: {output_data['posts_with_media']}")
    print(f"  - Posts with images: {output_data['posts_with_images']}")
        
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
