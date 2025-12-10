import requests
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone


# Configuration
TRACKER_USERNAME = os.getenv("TRACKER_USERNAME")
TRACKER_PASSWORD = os.getenv("TRACKER_PASSWORD")
API_BASE = "https://tracker.dtcc.chalmers.se/api"
OUTPUT_DIR = Path("public/content/papers")


def slugify(name):
    """Convert MSP name to slug (lowercase, hyphens)"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def create_session():
    """Create authenticated session using cookies"""
    session = requests.Session()

    url = f"{API_BASE}/auth/login"
    payload = {
        "username": TRACKER_USERNAME,
        "password": TRACKER_PASSWORD
    }

    response = session.post(url, json=payload)
    response.raise_for_status()

    data = response.json()
    if data.get("message") != "Login successful":
        raise Exception(f"Unexpected auth response: {data}")

    return session


def fetch_papers_by_milestone(session):
    """Fetch papers grouped by milestone"""
    url = f"{API_BASE}/papers/by-milestone"

    response = session.get(url)
    response.raise_for_status()

    return response.json()


def write_msp_file(msp_name, msp_data, timestamp):
    """Write a single MSP JSON file"""
    slug = slugify(msp_name)

    output = {
        "name": msp_name,
        "slug": slug,
        "count": msp_data.get("count", len(msp_data.get("papers", []))),
        "fetched_at": timestamp,
        "papers": [
            {
                "id": p.get("id"),
                "doi": p.get("doi"),
                "title": p.get("title"),
                "author_name": p.get("author_name"),
                "journal": p.get("journal"),
                "date": p.get("date"),
                "url": p.get("url"),
                "publication_type": p.get("publication_type"),
                "additional_authors": p.get("additional_authors", [])
            }
            for p in msp_data.get("papers", [])
        ]
    }

    filepath = OUTPUT_DIR / f"{slug}.json"
    with filepath.open('w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return filepath, slug


def main():
    # Check credentials
    if not TRACKER_USERNAME or not TRACKER_PASSWORD:
        print("Error: Missing environment variables")
        print("Required: TRACKER_USERNAME, TRACKER_PASSWORD")
        exit(1)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Fetching Papers by Milestone ===\n")

    # Authenticate
    print("Authenticating...")
    try:
        session = create_session()
        print("  Authenticated successfully\n")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in (401, 403):
            print("Error: Invalid credentials")
        else:
            print(f"Error: Authentication failed - {e}")
        exit(1)

    # Fetch papers
    print("Fetching papers...")
    try:
        data = fetch_papers_by_milestone(session)
        total_papers = data.get("total_papers", 0)
        milestones = data.get("milestones", {})
        print(f"  Found {total_papers} papers across {len(milestones)} milestones\n")
    except requests.exceptions.HTTPError as e:
        print(f"Error: Failed to fetch papers - {e}")
        exit(1)

    # Write files
    timestamp = datetime.now(timezone.utc).isoformat()
    files_written = []

    print("Writing JSON files...")
    for msp_name, msp_data in milestones.items():
        filepath, slug = write_msp_file(msp_name, msp_data, timestamp)
        paper_count = msp_data.get("count", len(msp_data.get("papers", [])))
        files_written.append((slug, paper_count))
        print(f"  {slug}.json ({paper_count} papers)")

    # Summary
    print("\n" + "=" * 50)
    print(f"Wrote {len(files_written)} files to {OUTPUT_DIR}/")
    print(f"Total papers: {total_papers}")


if __name__ == "__main__":
    main()
