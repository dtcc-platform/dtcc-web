DTCC Web — Content Posting Guide

Overview
- This project supports two ways to publish News and Projects:
  - Build-time from `src/<type>`: add matching `name.json` + `name.jpeg` (or `.jpg` / `.png`).
  - Runtime from `public/<type>`: a manifest at `public/<type>/index.json` (+ item JSONs). Runtime items override build-time ones.
  - `<type>` is `news` or `projects`.

Automated News Drafting
- Run `python3 news_item_wizard.py` to interactively draft runtime news items with Gemini Pro.
- Requirements:
  - `pip install google-generativeai`
  - `export GEMINI_API_KEY="<your token>"`
- The wizard collects headline + bullet points, calls Gemini for a JSON draft, lets you approve/adjust the URL/image, writes `public/content/news/<slug>.json`, and updates the manifest (`public/content/news/index.json`).
- If the generated file exists, the script asks before overwriting.
- This LLM-assisted workflow is experimental. Always review the draft carefully and make any edits needed before approving.
- Browser UI (`/chat/`): set `VITE_CHAT_AUTH_URL` and `VITE_CHAT_PUBLISH_URL` in `.env.local`, run `npm run dev`, visit `/chat/`, sign in, paste your Gemini API key, provide headline + bullets, and optionally connect the repo folder via the File System Access prompt to write files automatically (local mode still works when the publish URL is omitted). The session token expires (default 1 hour); when it does, the UI returns to the login screen.
- Without the auth URL the login gate refuses access (helpful if you want to disable the editor temporarily).
- The `/chat/` page keeps the site chrome but is hidden from navigation and marked `noindex`; share its URL only with trusted editors.
- If File System Access isn't available, download the JSON from the wizard and copy it into `public/content/news`, then update `index.json` manually.

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
   - To regenerate the manifest automatically, run `python3 scripts/update_news_projects_manifest.py` (CI runs this step during deploys for news & projects).

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
   - The same manifest helper `python3 scripts/update_news_projects_manifest.py` keeps this list in sync with the JSON files.

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
- The workflow auto-regenerates `public/content/news/index.json` and `public/content/projects/index.json`; if either manifest changes the GitHub Actions bot commits the update back to the repo before deploying.

Serverless Publisher (AWS Lambda)
- `infra/aws/publish_post_lambda.py` implements a Lambda handler that commits wizard output straight to GitHub through the REST API.
- Required environment variables:
  - `GITHUB_REPO` → `owner/repo`
  - `GITHUB_BRANCH` (optional, defaults to `main`)
  - Either `GITHUB_TOKEN` (fine-grained PAT with `contents:write`) or `GITHUB_TOKEN_SECRET_NAME` (Secrets Manager ID returning `{ "token": "..." }`).
  - `SESSION_SECRET` (matches the login Lambda)
  - `ALLOWED_ORIGIN` (e.g. `https://dtcc-platform.github.io` for GitHub Pages)
- Optional auth:
  - `SESSION_SECRET` (shared with the login Lambda) enables Bearer token verification.
  - `PUBLISHER_SHARED_SECRET` remains as a fallback `x-api-token` if you need static access.
- Deploy behind API Gateway (REST or HTTP) with CORS locked to the GitHub Pages origin. Grant the Lambda role permission to read the secret.
- Request payload (JSON body):
  ```
  {
    "section": "news",
    "slug": "example-post",
    "payload": { ...post JSON... },
    "force": false,
    "commitMessage": "Add News entry example-post",
    "imageUpload": {
      "filename": "example-post.jpg",
      "contentType": "image/jpeg",
      "data": "<base64 bytes>"
    }
  }
  ```
  `imageUpload` is optional; remote-image URLs should already be present in `payload.image`.
- On success the handler writes `public/content/<section>/<slug>.json`, uploads the image (if provided), updates `public/content/<section>/index.json`, and returns `{ "ok": true, "manifestUpdated": true }`.

Login API (AWS Lambda)
- `infra/aws/login_lambda.py` validates editor credentials and issues signed session tokens.
- Environment:
  - `LOGIN_USERNAME` / `LOGIN_PASSWORD`
  - `SESSION_SECRET` (must match the publisher Lambda)
  - `SESSION_TTL_SECONDS` (optional, default 3600)
  - `ALLOWED_ORIGIN` (same origin you allow in API Gateway CORS, e.g. `https://dtcc-platform.github.io`)
- Deploy behind API Gateway (REST). Require an API key if you want an extra gateway guard.
- Response shape:
  ```
  { "token": "<bearer token>", "expiresAt": 1735689600 }
  ```
- Point `VITE_CHAT_AUTH_URL` to this endpoint and `VITE_CHAT_PUBLISH_URL` to the publish API; the `/chat/` login form exchanges the credentials for the token and stores it in `sessionStorage` for later API calls.
