import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import urllib.error
import urllib.request

import boto3  # type: ignore


GITHUB_API_BASE = "https://api.github.com"

SECTION_CONFIG: Dict[str, Dict[str, str]] = {
    "news": {"content_dir": "news", "manifest_label": "News"},
    "events": {"content_dir": "events", "manifest_label": "Events"},
    "projects": {"content_dir": "projects", "manifest_label": "Projects"},
}


class LambdaError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _assert_authorized(event: Dict[str, Any]) -> None:
    headers = _normalize_headers(event.get("headers") or {})

    session_secret = os.getenv("SESSION_SECRET", "").strip()
    bearer = headers.get("authorization")
    token = _extract_bearer(bearer)
    if session_secret and token and _verify_session_token(token, session_secret):
        return

    static_secret = os.getenv("PUBLISHER_SHARED_SECRET", "").strip()
    if static_secret:
        api_token = headers.get("x-api-token")
        if api_token and hmac.compare_digest(api_token, static_secret):
            return

    raise LambdaError("Unauthorized", 401)


def _normalize_headers(headers: Dict[str, Any]) -> Dict[str, str]:
    normalized: Dict[str, str] = {}
    for key, value in headers.items():
        if not isinstance(key, str):
            continue
        if not isinstance(value, str):
            continue
        normalized[key.lower()] = value
    return normalized


def _extract_bearer(value: Optional[str]) -> Optional[str]:
    if not value or not isinstance(value, str):
        return None
    parts = value.strip().split(" ", 1)
    if len(parts) != 2:
        return None
    scheme, token = parts
    if scheme.lower() != "bearer":
        return None
    return token.strip() or None


def _verify_session_token(token: str, secret: str) -> bool:
    try:
        payload_segment, signature = token.split(".", 1)
    except ValueError:
        return False

    expected_sig = hmac.new(secret.encode("utf-8"), payload_segment.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return False

    try:
        payload_bytes = _urlsafe_b64decode(payload_segment)
        data = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return False

    exp = int(data.get("exp") or 0)
    if exp < int(time.time()):
        return False
    return True


def _urlsafe_b64decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for committing wizard output to GitHub.

    Expected payload (JSON body):
      {
        "section": "news" | "events" | "projects",
        "slug": "kebab-case-slug",
        "payload": { ... JSON document ... },
        "force": false,
        "imageUpload": {
          "filename": "slug.jpg",
          "contentType": "image/jpeg",
          "data": "base64-encoded-bytes"
        }
      }
    The `imageUpload` block is optional. When omitted, the handler leaves the manifest
    entry untouched. For remote images just set payload.image to the remote URL on the client.
    """
    try:
        _assert_authorized(event)
        data = _parse_event(event)
        config = _resolve_section(data["section"])
        token = _resolve_github_token()
        client = _GitHubClient(token=token)

        content_path = f"public/content/{config.content_dir}/{data['slug']}.json"
        image_upload = data.get("imageUpload")

        commit_message = data.get("commitMessage") or _default_commit_message(
            section=data["section"], slug=data["slug"]
        )

        json_bytes = _dump_json_bytes(data["payload"])
        client.put_file(
            path=content_path,
            blob=json_bytes,
            message=commit_message,
            force=data.get("force", False),
        )

        if image_upload:
            image_path, image_bytes = _prepare_image_upload(
                image_upload, config.content_dir, data["slug"]
            )
            client.put_file(
                path=image_path,
                blob=image_bytes,
                message=commit_message,
                force=data.get("force", False),
            )
            manifest_image_ref = f"content/{config.content_dir}/{os.path.basename(image_path)}"
        else:
            manifest_image_ref = _extract_manifest_image(data["payload"])

        manifest_path = f"public/content/{config.content_dir}/index.json"
        manifest = client.get_json_file(manifest_path) or {"items": []}
        updated_manifest, changed = _update_manifest(
            manifest,
            section=data["section"],
            slug=data["slug"],
            payload=data["payload"],
            image=manifest_image_ref,
            force=data.get("force", False),
        )

        if changed:
            manifest_bytes = _dump_json_bytes(updated_manifest)
            client.put_file(
                path=manifest_path,
                blob=manifest_bytes,
                message=commit_message,
                force=True,
            )

        return _response(200, {"ok": True, "manifestUpdated": changed})
    except LambdaError as err:
        return _response(err.status_code, {"error": str(err)})
    except Exception as exc:  # pragma: no cover - catch all
        return _response(500, {"error": "Unhandled server error", "detail": str(exc)})


def _parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if "body" not in event:
        raise LambdaError("Missing request body", 400)

    body = event["body"]
    if event.get("isBase64Encoded"):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise LambdaError(f"Invalid base64 body: {exc}", 400)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise LambdaError(f"Body must be valid JSON: {exc}", 400)

    if not isinstance(payload, dict):
        raise LambdaError("Body must be a JSON object", 400)

    section = payload.get("section")
    if section not in SECTION_CONFIG:
        raise LambdaError("Invalid 'section' field", 400)

    slug = payload.get("slug")
    if not slug or not isinstance(slug, str):
        raise LambdaError("Missing or invalid 'slug'", 400)

    draft = payload.get("payload")
    if not isinstance(draft, dict):
        raise LambdaError("Missing 'payload' JSON object", 400)

    image_upload = payload.get("imageUpload")
    if image_upload is not None:
        _validate_image_upload(image_upload)

    return {
        "section": section,
        "slug": slug,
        "payload": draft,
        "force": bool(payload.get("force")),
        "imageUpload": image_upload,
        "commitMessage": payload.get("commitMessage"),
    }


def _validate_image_upload(image_upload: Dict[str, Any]) -> None:
    if not isinstance(image_upload, dict):
        raise LambdaError("'imageUpload' must be an object", 400)
    if "data" not in image_upload:
        raise LambdaError("'imageUpload.data' is required", 400)

    try:
        base64.b64decode(image_upload["data"])
    except (ValueError, TypeError) as exc:
        raise LambdaError(f"Image data must be base64 encoded: {exc}", 400)


def _resolve_section(section: str) -> "SectionContext":
    cfg = SECTION_CONFIG.get(section)
    if not cfg:
        raise LambdaError("Unsupported section", 400)
    return SectionContext(
        section=section,
        content_dir=cfg["content_dir"],
        manifest_label=cfg["manifest_label"],
    )


def _resolve_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN")
    secret_name = os.getenv("GITHUB_TOKEN_SECRET_NAME")

    if secret_name:
        client = boto3.client("secretsmanager")
        secret_value = client.get_secret_value(SecretId=secret_name)
        secret_string = secret_value.get("SecretString") or ""
        if not secret_string:
            raise LambdaError("GitHub token secret is empty", 500)
        try:
            maybe_json = json.loads(secret_string)
            token = maybe_json.get("token") or maybe_json.get("access_token") or token
        except json.JSONDecodeError:
            token = secret_string or token

    if not token:
        raise LambdaError("GitHub token not configured", 500)

    return token


def _dump_json_bytes(payload: Dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _prepare_image_upload(
    image_upload: Dict[str, Any], section_dir: str, slug: str
) -> Tuple[str, bytes]:
    filename = image_upload.get("filename") or f"{slug}.jpg"
    content_type = image_upload.get("contentType") or "application/octet-stream"

    raw_bytes = base64.b64decode(image_upload["data"])
    # Guard against accidental JSON/text uploads
    if len(raw_bytes) == 0:
        raise LambdaError("Uploaded image contains no data", 400)

    path = f"public/content/{section_dir}/{filename}"
    # Prevent directory traversal
    normalized_path = "/".join(part for part in path.split("/") if part not in ("", ".", ".."))
    if not normalized_path.startswith(f"public/content/{section_dir}/"):
        raise LambdaError("Invalid image path", 400)

    return normalized_path, raw_bytes


def _extract_manifest_image(payload: Dict[str, Any]) -> str:
    image = payload.get("image")
    if isinstance(image, str) and image.strip():
        return image.strip()
    return ""


def _update_manifest(
    manifest: Dict[str, Any],
    *,
    section: str,
    slug: str,
    payload: Dict[str, Any],
    image: str,
    force: bool,
) -> Tuple[Dict[str, Any], bool]:
    items = manifest.get("items")
    if not isinstance(items, list):
        raise LambdaError("Manifest must contain an array under 'items'", 500)

    changed = False

    if section in ("news", "projects"):
        new_entry: Dict[str, Any]
        if image:
            new_entry = {"base": slug, "image": image}
        else:
            new_entry = {"base": slug}
        index = _find_manifest_index(items, slug)
        if index is None:
            manifest["items"].append(new_entry)
            changed = True
        elif force:
            manifest["items"][index] = _merge_manifest_entry(items[index], new_entry)
            changed = True
    else:
        new_entry = {
            "id": slug,
            "title": payload.get("title") or slug,
        }
        if payload.get("date"):
            new_entry["date"] = payload["date"]
        for key in ("timeStart", "timeEnd", "location", "meta"):
            if payload.get(key):
                new_entry[key] = payload[key]
        index = _find_manifest_index(items, slug)
        if index is None:
            manifest["items"].append(new_entry)
            changed = True
        elif force:
            merged = dict(items[index]) if isinstance(items[index], dict) else {}
            merged.update(new_entry)
            manifest["items"][index] = merged
            changed = True

    return manifest, changed


def _find_manifest_index(items: Any, slug: str) -> Optional[int]:
    for idx, entry in enumerate(items):
        if isinstance(entry, str) and entry == slug:
            return idx
        if isinstance(entry, dict):
            key = entry.get("base") or entry.get("id") or entry.get("slug")
            if key == slug:
                return idx
    return None


def _merge_manifest_entry(existing: Any, new_entry: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(existing, dict):
        merged = dict(existing)
        merged.update(new_entry)
        return merged
    return new_entry


def _default_commit_message(section: str, slug: str) -> str:
    label = SECTION_CONFIG.get(section, {}).get("manifest_label", section.title())
    return f"Add {label} entry {slug}"


def _response(status: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    origin = os.getenv("ALLOWED_ORIGIN", "*")
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        },
        "body": json.dumps(payload),
    }


@dataclass
class SectionContext:
    section: str
    content_dir: str
    manifest_label: str


class _GitHubClient:
    def __init__(self, *, token: str) -> None:
        repo = os.getenv("GITHUB_REPO")
        if not repo or "/" not in repo:
            raise LambdaError("GITHUB_REPO env var must be set to 'owner/repo'", 500)
        self.owner, self.repo = repo.split("/", 1)
        self.branch = os.getenv("GITHUB_BRANCH", "main")
        self.token = token

    def get_json_file(self, path: str) -> Optional[Dict[str, Any]]:
        response = self._request("GET", path)
        if response["status"] == 404:
            return None
        if response["status"] >= 400:
            raise LambdaError(f"Failed to load {path}: {response['body']}", 502)
        payload = json.loads(response["body"])
        if "content" not in payload:
            return None
        decoded = base64.b64decode(payload["content"])
        return json.loads(decoded.decode("utf-8"))

    def put_file(self, path: str, blob: bytes, message: str, *, force: bool) -> None:
        existing = self._request("GET", path)
        sha: Optional[str] = None
        if existing["status"] == 200:
            payload = json.loads(existing["body"])
            sha = payload.get("sha")
            if not force and sha:
                raise LambdaError(f"{path} already exists. Enable overwrite to replace it.", 409)
        elif existing["status"] not in (200, 404):
            raise LambdaError(f"Unable to inspect {path}: {existing['body']}", 502)

        encoded = base64.b64encode(blob).decode("utf-8")
        body = json.dumps(
            {
                "message": message,
                "content": encoded,
                "branch": self.branch,
                **({"sha": sha} if sha else {}),
            }
        ).encode("utf-8")
        upload = self._request("PUT", path, body=body)
        if upload["status"] >= 300:
            raise LambdaError(f"Failed to write {path}: {upload['body']}", 502)

    def _request(self, method: str, path: str, body: Optional[bytes] = None) -> Dict[str, Any]:
        url = f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}/contents/{path}"
        req = urllib.request.Request(url, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "dtcc-web-publish-lambda")
        if body is not None:
            req.add_header("Content-Type", "application/json")
            req.data = body

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                payload = resp.read().decode("utf-8")
                return {"status": resp.status, "body": payload}
        except urllib.error.HTTPError as err:
            return {"status": err.code, "body": err.read().decode("utf-8")}
        except urllib.error.URLError as err:
            raise LambdaError(f"GitHub API request failed: {err}", 502)
