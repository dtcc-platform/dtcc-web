#!/usr/bin/env python3
"""Draft DTCC news items with Gemini from the CLI or an HTTP API."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DraftContext:
    title: str
    summary_points: str
    slug: str
    tone: Optional[str]


class DraftError(RuntimeError):
    """Raised when a draft cannot be generated or parsed."""


RE_WHITESPACE = re.compile(r"\s+")


def ensure_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise DraftError(
            "Set the GEMINI_API_KEY environment variable with your Gemini API token."
        )
    return api_key


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9\-\s]", "", value)
    value = RE_WHITESPACE.sub("-", value).strip("-")
    value = re.sub(r"-+", "-", value)
    return value or "news-entry"


def gather_context() -> DraftContext:
    print("DTCC News Draft Helper\n------------------------")
    title = input("Headline (required): ").strip()
    if not title:
        raise DraftError("A headline is required to describe the news item.")

    print(
        "\nAdd a few bullet points describing the announcement."
        " Press ENTER on an empty line to finish."
    )
    bullet_lines: List[str] = []
    while True:
        try:
            line = input(" • ")
        except EOFError:
            line = ""
        if not line.strip():
            break
        bullet_lines.append(line.strip())

    if not bullet_lines:
        raise DraftError("At least one supporting bullet point is required.")

    default_slug = slugify(title)
    slug = input(f"Base file name (slug) [{default_slug}]: ").strip() or default_slug
    tone = input("Optional tone guidance (e.g. formal, excited) [skip]: ").strip() or None

    bullet_text = "\n".join(f"- {line}" for line in bullet_lines)

    return DraftContext(title=title, summary_points=bullet_text, slug=slug, tone=tone)


def load_gemini_model(api_key: str):
    try:
        import google.generativeai as genai
    except ImportError as exc:  # pragma: no cover - import guard
        raise DraftError(
            "Install the google-generativeai package: pip install google-generativeai"
        ) from exc

    genai.configure(api_key=api_key)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
    return genai.GenerativeModel(model_name)


def request_draft(model: Any, context: DraftContext) -> Dict[str, Any]:
    tone_clause = (
        f"Match this tone: {context.tone}."
        if context.tone
        else "Maintain the professional-yet-approachable tone of an architectural firm."
    )

    prompt = f"""
You help prepare runtime news items for the DTCC marketing site.
Follow the "DTCC Web — Content Posting Guide" requirements for public/content/news/*.json entries.

Constraints:
- Output must be a single JSON object compatible with JSON.parse.
- Include keys only when they offer value. Required key: "title".
- Prefer ISO date format (YYYY-MM-DD) when a specific date is implied.
- Use the provided slug `{context.slug}` to build any internal URLs (e.g. "/news/{context.slug}").
- Suggest an image URL under the `image` key if you can reference a relevant royalty-free photograph.
- Limit the summary to ~40 words.
- {tone_clause}

Inputs:
- Headline: {context.title}
- Supporting details:\n{context.summary_points}

Return only the JSON object, nothing else.
"""

    generation_config = {
        "temperature": 0.45,
        "response_mime_type": "application/json",
    }

    response = model.generate_content(prompt, generation_config=generation_config)

    if not response or not getattr(response, "text", "").strip():
        raise DraftError("No response received from Gemini.")

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as exc:  # pragma: no cover - runtime guard
        raise DraftError(f"Gemini returned invalid JSON: {response.text}") from exc


def confirm(prompt: str) -> bool:
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def repo_paths() -> Dict[str, Path]:
    root = Path(__file__).resolve().parent
    news_dir = root / "public" / "content" / "news"
    manifest_path = news_dir / "index.json"
    return {"root": root, "news_dir": news_dir, "manifest": manifest_path}


def write_item(
    slug: str,
    data: Dict[str, Any],
    news_dir: Path,
    *,
    force: bool = False,
    interactive: bool = True,
) -> Path:
    news_dir.mkdir(parents=True, exist_ok=True)
    item_path = news_dir / f"{slug}.json"

    if item_path.exists() and not force:
        if interactive:
            print(f"Warning: {item_path} already exists.")
            if not confirm("Overwrite existing file?"):
                raise DraftError("Aborted before overwriting existing news item.")
        else:
            raise DraftError(
                f"{item_path} already exists. Retry with 'force' enabled to overwrite."
            )

    with item_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=True, indent=2)
        fh.write("\n")

    return item_path


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError as exc:
                raise DraftError(f"Cannot parse manifest {manifest_path}: {exc}") from exc
    return {"items": []}


def manifest_contains(items: List[Any], slug: str) -> bool:
    for entry in items:
        if isinstance(entry, str) and entry == slug:
            return True
        if isinstance(entry, dict) and entry.get("base") == slug:
            return True
    return False


def update_manifest(
    manifest_path: Path, slug: str, image: Optional[str], *, quiet: bool = False
) -> bool:
    manifest = load_manifest(manifest_path)
    items = manifest.setdefault("items", [])

    if not isinstance(items, list):
        raise DraftError(f"Manifest {manifest_path} should contain a list under 'items'.")

    if manifest_contains(items, slug):
        if not quiet:
            print(f"Manifest already references '{slug}'. Skipping manifest update.")
        return False

    entry: Any = {"base": slug}
    if image:
        entry["image"] = image

    items.append(entry)

    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=True, indent=2)
        fh.write("\n")

    return True


def run_cli() -> None:
    try:
        context = gather_context()
        api_key = ensure_api_key()
        model = load_gemini_model(api_key)
        draft = request_draft(model, context)
    except DraftError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)

    print("\nGemini draft:\n--------------")
    print(json.dumps(draft, indent=2, ensure_ascii=False))

    if not confirm("Accept this draft?"):
        print("Draft discarded.")
        return

    if "url" not in draft:
        default_url = f"/news/{context.slug}"
        if confirm(f"Add default URL '{default_url}'?"):
            draft["url"] = default_url

    image = draft.get("image")
    if not image:
        fallback = input("Optional image path or URL for the manifest [skip]: ").strip()
        if fallback:
            image = fallback

    paths = repo_paths()
    try:
        item_path = write_item(context.slug, draft, paths["news_dir"], interactive=True)
        update_manifest(paths["manifest"], context.slug, image)
    except DraftError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("\nSaved new news item at:")
    print(f" - Metadata: {item_path}")
    print(f" - Manifest: {paths['manifest']}")


def create_service(model: Any):  # pragma: no cover - HTTP server helper
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel, Field, validator
    except ImportError as exc:
        raise DraftError(
            "Install FastAPI support: pip install fastapi uvicorn[standard]"
        ) from exc

    paths = repo_paths()

    app = FastAPI(title="DTCC News Wizard", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.environ.get("NEWS_WIZARD_ALLOW_ORIGINS", "*").split(","),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class DraftPayload(BaseModel):
        title: str
        bullets: List[str]
        slug: Optional[str] = None
        tone: Optional[str] = None

        @validator("title")
        def clean_title(cls, value: str) -> str:
            value = value.strip()
            if not value:
                raise ValueError("Title is required")
            return value

        @validator("bullets")
        def clean_bullets(cls, values: List[str]) -> List[str]:
            cleaned = [line.strip() for line in values if line and line.strip()]
            if not cleaned:
                raise ValueError("Provide at least one supporting bullet point")
            return cleaned

    class SavePayload(BaseModel):
        slug: str
        payload: Dict[str, Any]
        manifest_image: Optional[str] = Field(default=None, alias="manifestImage")
        force: bool = False

        @validator("slug")
        def clean_slug(cls, value: str) -> str:
            value = slugify(value)
            if not value:
                raise ValueError("Slug is required")
            return value

        @validator("payload")
        def ensure_title(cls, value: Dict[str, Any]) -> Dict[str, Any]:
            if not isinstance(value, dict) or not value.get("title"):
                raise ValueError("payload.title is required")
            return value

    @app.post("/api/news/draft")
    def draft_news(payload: DraftPayload):
        slug = slugify(payload.slug or payload.title)
        bullet_text = "\n".join(f"- {line}" for line in payload.bullets)
        context = DraftContext(
            title=payload.title,
            summary_points=bullet_text,
            slug=slug,
            tone=payload.tone or None,
        )
        try:
            draft = request_draft(model, context)
        except DraftError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {"slug": slug, "draft": draft}

    @app.post("/api/news/save")
    def save_news(payload: SavePayload):
        image = payload.manifest_image or payload.payload.get("image")
        try:
            item_path = write_item(
                payload.slug,
                payload.payload,
                paths["news_dir"],
                force=payload.force,
                interactive=False,
            )
            update_manifest(paths["manifest"], payload.slug, image, quiet=True)
        except DraftError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return {
            "itemPath": str(item_path.relative_to(paths["root"])),
            "manifestPath": str(paths["manifest"].relative_to(paths["root"])),
        }

    @app.get("/api/news/health")
    def healthcheck():
        return {"status": "ok", "newsDir": str(paths["news_dir"]) }

    return app


def run_server(host: str, port: int) -> None:
    try:
        api_key = ensure_api_key()
        model = load_gemini_model(api_key)
        app = create_service(model)
    except DraftError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - import guard
        print("Install uvicorn to run the API server: pip install uvicorn[standard]", file=sys.stderr)
        sys.exit(1)

    uvicorn.run(app, host=host, port=port)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__ or "News drafting helper")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Run an HTTP API instead of the interactive CLI",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for --serve mode")
    parser.add_argument("--port", type=int, default=8000, help="Bind port for --serve mode")
    args = parser.parse_args()

    if args.serve:
        run_server(args.host, args.port)
    else:
        run_cli()


if __name__ == "__main__":
    main()

