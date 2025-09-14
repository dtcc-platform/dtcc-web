DTCC Web — Content Posting Guide

Overview
- This project supports two ways to publish News and Projects:
  - Build‑time from `src/<type>`: add matching `name.json` + `name.jpeg` (or `.jpg` / `.png`).
  - Runtime from `public/<type>`: a manifest at `public/<type>/index.json` (+ item JSONs). Runtime items override build‑time ones.
  - `<type>` is `news` or `projects`.

News — Quick Start (Runtime — recommended)
1) Add/Update the manifest at `public/content/news/index.json`.
   - Use either an array of base names or objects.
   - Base name refers to the `public/news/<base>.json` metadata file.
   - Example:
     {
       "items": [
         { "base": "webinar-june12", "image": "/news/webinar-june12.jpeg" },
         { "base": "extension-2025", "image": "https://example.com/cover.jpg" }
       ]
     }

2) Create per‑item JSON files in `public/content/news/` with the same base name:
   - Required: `title`
   - Optional: `summary` (or `excerpt`), `url` (or `link`), `date` (ISO or parsable), `eyebrow`, `image`
   - Example `public/content/news/webinar-june12.json`:
     {
       "title": "Create tool webinar — Join us on June 12th",
       "summary": "A short intro for the webinar and how to sign up.",
       "url": "/news/webinar-june12",
       "date": "2025-06-12",
       "eyebrow": "News"
     }

3) Provide an image for each item.
   - Preferred: Set `image` in the manifest or in the item JSON (absolute path like `/content/news/<base>.jpeg` or external URL).
   - If `image` is not set, the app will probe for `/content/news/<base>.jpeg`, then `.jpg`, then `.png`.
   - External images are allowed (CORS permitting). If your server blocks HEAD requests, set `image` explicitly to avoid probing.

News — Build‑Time Source (Alternative)
- Place `src/news/<name>.json` and matching `src/news/<name>.(jpeg|jpg|png)`.
- During build, the app will bundle and publish items that have both files.
- Fields are the same as the runtime JSON. Items sort by `date` descending if provided.

Projects — Quick Start (Runtime — recommended)
1) Add/Update the manifest at `public/content/projects/index.json`.
   - Format mirrors News: either an array of base names or an array of objects with overrides.
   - Examples:
     {
       "items": [
         { "base": "urban-comfort", "image": "/projects/urban-comfort.jpeg" },
         { "base": "underground-4d", "image": "https://example.com/cover.jpg" }
       ]
     }

2) Create per‑item JSON files in `public/content/projects/` with the same base name:
   - Required: `title`
   - Optional: `summary` | `excerpt` | `description`, `url` | `link`, `date`, `image`
   - Example `public/projects/urban-comfort.json`:
     {
       "title": "Urban Environmental Comfort Design",
       "summary": "Urban densification influences wind, temperature, noise, daylight and air quality at both city scale and …",
       "url": "/projects/urban-comfort",
       "date": "2025-03-02"
     }

3) Provide an image for each project.
   - Preferred: Set `image` in the manifest or item JSON.
   - If not set, the app probes `/content/projects/<base>.jpeg`, then `.jpg`, then `.png`.

Projects — Build‑Time Source (Alternative)
- Place `src/projects/<name>.json` and matching `src/projects/<name>.(jpeg|jpg|png)`.
- Bundled at build if both files exist. Sorted by `date` descending when present.

Fields Reference
- title: string (required)
- summary | excerpt | description: string (optional)
- url | link: string (optional) — link target for “Read more »”
- date | published | publishedAt | time: string (optional) — any parsable date format
- eyebrow: string (optional) — defaults to “News”
- image: string (optional) — URL or absolute path under `/news/`

Hero Carousel Notes
- Slide titles are defined in `src/components/HeroSection.vue` (`slides` array).
- Supports background `image` or looping `video` per slide.
- Auto‑advance interval can be set with `<HeroSection :interval-sec="6" />`.
 - Current config: Auto‑advance disabled; slide 1 video plays once.

Local Development
- Install deps: `npm install`
- Start dev server: `npm run dev`
- Build production: `npm run build` (output in `dist/`)

Deployment — GitHub Pages
- This repo includes a GitHub Actions workflow at `.github/workflows/deploy.yml` that builds and publishes the site to GitHub Pages.
- Steps to enable:
  1) Push the repo to GitHub.
  2) In GitHub → Settings → Pages, set Source to “GitHub Actions”.
  3) Ensure your default branch is `main` (or `master`); the workflow listens to both.
- Vite `base` path is auto-configured for project pages:
  - When building on GitHub Actions, `vite.config.js` sets `base` to `/<repo>/`.
  - When running locally, `base` is `/` so local dev isn’t affected.
- After the workflow runs, your site is available at:
  - Project page: `https://<user>.github.io/<repo>/`
  - User/Org page (if using `<user>.github.io` repo): `https://<user>.github.io/`
