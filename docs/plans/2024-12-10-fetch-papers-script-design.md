# Fetch Papers Script Design

## Overview

Standalone Python script to fetch papers from tracker.dtcc.chalmers.se API and store them as JSON files grouped by Milestone Project (MSP).

## Configuration

**File:** `scripts/fetch_papers.py`

**Environment variables:**
- `TRACKER_USERNAME` - API username
- `TRACKER_PASSWORD` - API password

**Output location:** `public/content/papers/`

## API Endpoints Used

**Authentication:**
```
POST https://tracker.dtcc.chalmers.se/api/auth/login/
Content-Type: application/json
Body: {"username": "...", "password": "..."}
```

**Fetch papers:**
```
GET https://tracker.dtcc.chalmers.se/api/papers/by-milestone/
Authorization: Bearer <token>
```

## Script Flow

1. Read credentials from environment variables
   - Exit with clear error if missing
2. Authenticate via POST /api/auth/login/
   - Extract access token from response
3. Fetch papers via GET /api/papers/by-milestone/
4. For each milestone in response:
   - Slugify the MSP name (e.g., "Digital twin platform" -> "digital-twin-platform")
   - Write to `public/content/papers/<slug>.json`
5. Print summary (files written, total papers)

## Output Structure

One JSON file per MSP. Example `digital-twin-platform.json`:

```json
{
  "name": "Digital twin platform",
  "slug": "digital-twin-platform",
  "count": 12,
  "fetched_at": "2024-12-10T14:30:00Z",
  "papers": [
    {
      "id": 1,
      "doi": "10.1234/example.123",
      "title": "Example Paper Title",
      "author_name": "John Smith",
      "journal": "Journal of Digital Twins",
      "date": "2024-05-15",
      "url": "https://example.com/paper",
      "publication_type": "Article in journal",
      "additional_authors": ["Jane Doe", "Bob Wilson"]
    }
  ]
}
```

Files created will include:
- `digital-twin-platform.json`
- `twinable.json`
- `ai-3d-city-modeling.json`
- `unassigned.json`
- (etc., one per MSP)

## Error Handling

- **Missing env vars:** Exit with message listing required variables
- **Auth failure (401/403):** Exit with "Invalid credentials" message
- **Network errors:** Exit with error details
- **Empty milestone (0 papers):** Still write file with empty `papers` array

## Idempotency

- Script overwrites existing files on each run (no merge)
- Safe to run repeatedly (e.g., via CI/cron)
