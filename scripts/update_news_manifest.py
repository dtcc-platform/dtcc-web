#!/usr/bin/env python3
"""
Regenerate public/content/news/index.json from per-item JSON files.

The manifest is sorted by date descending (if provided) and falls back to slug order.
Each entry includes the image field only when present in the source JSON.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


ROOT_DIR = Path(__file__).resolve().parents[1]
NEWS_DIR = ROOT_DIR / "public" / "content" / "news"
MANIFEST_PATH = NEWS_DIR / "index.json"


def load_existing_manifest() -> Dict[str, Dict[str, Any]]:
    if not MANIFEST_PATH.exists():
        return {}
    try:
        with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}

    items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return {}

    result: Dict[str, Dict[str, Any]] = {}
    for item in items:
        if isinstance(item, str):
            result[item] = {}
            continue
        if not isinstance(item, dict):
            continue
        slug = item.get("base") or item.get("id") or item.get("slug") or item.get("name")
        if not isinstance(slug, str) or not slug:
            continue
        result[slug] = {k: v for k, v in item.items() if k != "base"}
    return result


def load_news_items() -> Iterable[Tuple[str, Dict[str, Any]]]:
    for path in sorted(NEWS_DIR.glob("*.json")):
        if path.name == "index.json":
            continue
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        yield path.stem, data


def parse_date(data: Dict[str, Any]) -> date | None:
    candidates = (
        data.get("date")
        or data.get("published")
        or data.get("publishedAt")
        or data.get("time")
    )
    if not candidates:
        return None
    value = str(candidates).strip()
    if not value:
        return None
    try:
        # Handles YYYY-MM-DD and trims ISO timestamps to date
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def build_manifest_items(existing: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    records: List[Tuple[date | None, str, Dict[str, Any]]] = []
    for slug, payload in load_news_items():
        entry: Dict[str, Any] = {"base": slug}
        image = payload.get("image")
        if isinstance(image, str) and image.strip():
            entry["image"] = image.strip()
        extras = existing.get(slug, {})
        if "image" not in entry and isinstance(extras.get("image"), str) and extras["image"].strip():
            entry["image"] = extras["image"].strip()
        for key, value in extras.items():
            if key in ("base", "image"):
                continue
            if key not in entry and value not in (None, ""):
                entry[key] = value
        record_date = parse_date(payload)
        records.append((record_date, slug, entry))

    def sort_key(item: Tuple[date | None, str, Dict[str, Any]]) -> Tuple[int, int, str]:
        record_date, slug, _ = item
        if record_date:
            return (0, -record_date.toordinal(), slug)
        return (1, 0, slug)

    records.sort(key=sort_key)
    return [entry for _, _, entry in records]


def main() -> None:
    if not NEWS_DIR.exists():
        raise SystemExit(f"Missing directory: {NEWS_DIR}")

    existing_manifest = load_existing_manifest()
    manifest = {"items": build_manifest_items(existing_manifest)}
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    existing = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else ""
    if existing == rendered:
        print("News manifest is up to date.")
        return

    MANIFEST_PATH.write_text(rendered, encoding="utf-8")
    print(f"Updated {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
