#!/usr/bin/env python3
"""
Regenerate content manifests for runtime news and projects entries.

Each section scans `public/content/<section>/*.json`, rebuilds the matching
`index.json`, and preserves existing manifest extras (images, order, etc.).
New entries are reported in the console so CI logs stay informative.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


ROOT_DIR = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT_DIR / "public" / "content"

SECTION_SETTINGS: Dict[str, Dict[str, Any]] = {
    "news": {
        "dir": "news",
        "date_fields": ("date", "published", "publishedAt", "time"),
    },
    "projects": {
        "dir": "projects",
        "date_fields": ("date", "published", "publishedAt", "updated"),
    },
}


def load_existing_manifest(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
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
        slug = (
            item.get("base")
            or item.get("id")
            or item.get("slug")
            or item.get("name")
        )
        if not isinstance(slug, str) or not slug:
            continue
        result[slug] = {k: v for k, v in item.items() if k != "base"}
    return result


def load_content_items(dir_path: Path) -> Iterable[Tuple[str, Dict[str, Any]]]:
    for path in sorted(dir_path.glob("*.json")):
        if path.name == "index.json":
            continue
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        yield path.stem, data


def parse_date(payload: Dict[str, Any], fields: Sequence[str]) -> date | None:
    for field in fields:
        value = payload.get(field)
        if not value:
            continue
        text = str(value).strip()
        if not text:
            continue
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            continue
    return None


def build_manifest_entries(
    slug: str,
    payload: Dict[str, Any],
    existing_extras: Dict[str, Any],
) -> Dict[str, Any]:
    entry: Dict[str, Any] = {"base": slug}

    image = payload.get("image")
    if isinstance(image, str) and image.strip():
        entry["image"] = image.strip()
    elif isinstance(existing_extras.get("image"), str) and existing_extras["image"].strip():
        entry["image"] = existing_extras["image"].strip()

    for key, value in existing_extras.items():
        if key == "image":
            continue
        if key == "base":
            continue
        if key not in entry and value not in (None, ""):
            entry[key] = value

    return entry


def update_section(section: str) -> None:
    settings = SECTION_SETTINGS[section]
    dir_path = CONTENT_ROOT / settings["dir"]
    manifest_path = dir_path / "index.json"

    if not dir_path.exists():
        print(f"[{section}] Skipped: missing directory {dir_path}")
        return

    existing_manifest = load_existing_manifest(manifest_path)
    records: List[Tuple[date | None, str, Dict[str, Any]]] = []
    added: List[Tuple[str, str]] = []

    for slug, payload in load_content_items(dir_path):
        extras = existing_manifest.get(slug, {})
        entry = build_manifest_entries(slug, payload, extras)

        title = str(payload.get("title") or payload.get("name") or slug).strip() or slug
        if slug not in existing_manifest:
            added.append((slug, title))

        record_date = parse_date(payload, settings["date_fields"])
        records.append((record_date, slug, entry))

    def sort_key(item: Tuple[date | None, str, Dict[str, Any]]) -> Tuple[int, int, str]:
        record_date, slug, _ = item
        if record_date:
            return (0, -record_date.toordinal(), slug)
        return (1, 0, slug)

    records.sort(key=sort_key)
    manifest = {"items": [entry for _, _, entry in records]}

    rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    existing_text = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else ""

    if existing_text == rendered:
        print(f"[{section}] Manifest is up to date.")
        return

    manifest_path.write_text(rendered, encoding="utf-8")
    print(f"[{section}] Updated {manifest_path}")
    if added:
        print(f"[{section}] New items added:")
        for slug, title in added:
            print(f"  - {slug}: {title}")


def main() -> None:
    for section in SECTION_SETTINGS:
        update_section(section)


if __name__ == "__main__":
    main()
