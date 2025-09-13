DTCC Web — Content Posting Guide

Overview
- This project supports two ways to publish News items:
  - Build‑time from `src/news`: add matching `name.json` + `name.jpeg` (or `.jpg` / `.png`).
  - Runtime from `public/news`: a manifest at `public/news/index.json` (+ item JSONs). Runtime items override build‑time ones.

Quick Start (Runtime — recommended)
1) Add/Update the manifest at `public/news/index.json`.
   - Use either an array of base names or objects.
   - Base name refers to the `public/news/<base>.json` metadata file.
   - Example:
     {
       "items": [
         { "base": "webinar-june12", "image": "/news/webinar-june12.jpeg" },
         { "base": "extension-2025", "image": "https://example.com/cover.jpg" }
       ]
     }

2) Create per‑item JSON files in `public/news/` with the same base name:
   - Required: `title`
   - Optional: `summary` (or `excerpt`), `url` (or `link`), `date` (ISO or parsable), `eyebrow`, `image`
   - Example `public/news/webinar-june12.json`:
     {
       "title": "Create tool webinar — Join us on June 12th",
       "summary": "A short intro for the webinar and how to sign up.",
       "url": "/news/webinar-june12",
       "date": "2025-06-12",
       "eyebrow": "News"
     }

3) Provide an image for each item.
   - Preferred: Set `image` in the manifest or in the item JSON (absolute path like `/news/<base>.jpeg` or external URL).
   - If `image` is not set, the app will probe for `/news/<base>.jpeg`, then `.jpg`, then `.png`.
   - External images are allowed (CORS permitting). If your server blocks HEAD requests, set `image` explicitly to avoid probing.

Build‑Time Source (Alternative)
- Place `src/news/<name>.json` and matching `src/news/<name>.(jpeg|jpg|png)`.
- During build, the app will bundle and publish items that have both files.
- Fields are the same as the runtime JSON. Items sort by `date` descending if provided.

Fields Reference
- title: string (required)
- summary | excerpt: string (optional)
- url | link: string (optional) — link target for “Read more »”
- date | published | publishedAt | time: string (optional) — any parsable date format
- eyebrow: string (optional) — defaults to “News”
- image: string (optional) — URL or absolute path under `/news/`

Hero Carousel Notes
- Slide titles are defined in `src/components/HeroSection.vue` (`slides` array).
- Supports background `image` or looping `video` per slide.
- Auto‑advance interval can be set with `<HeroSection :interval-sec="6" />`.

Local Development
- Install deps: `npm install`
- Start dev server: `npm run dev`
- Build production: `npm run build` (output in `dist/`)

