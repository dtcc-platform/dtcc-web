import base64
import json
import os
import time
import hmac
import hashlib
from typing import Any, Dict


class AuthError(Exception):
    def __init__(self, message: str, status: int = 401) -> None:
        super().__init__(message)
        self.status = status


def handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    try:
        payload = _parse_event(event)
        token, expires_at = _authenticate(payload["username"], payload["password"])
        return _response(200, {"token": token, "expiresAt": expires_at})
    except AuthError as err:
        return _response(err.status, {"error": str(err)})
    except Exception as exc:  # pragma: no cover - catch all
        return _response(500, {"error": "Unhandled server error", "detail": str(exc)})


def _parse_event(event: Dict[str, Any]) -> Dict[str, str]:
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise AuthError(f"Invalid base64 body: {exc}", 400)

    try:
        payload = json.loads(body or "{}")
    except json.JSONDecodeError as exc:
        raise AuthError(f"Body must be valid JSON: {exc}", 400)

    username = str(payload.get("username") or "").strip()
    password = str(payload.get("password") or "")
    if not username or not password:
        raise AuthError("Username and password are required.", 400)

    return {"username": username, "password": password}


def _authenticate(username: str, password: str) -> tuple[str, int]:
    expected_username = os.getenv("LOGIN_USERNAME", "").strip()
    expected_password = os.getenv("LOGIN_PASSWORD", "")
    if not expected_username or not expected_password:
        raise AuthError("Login is not configured.", 500)

    if not (
        hmac.compare_digest(username, expected_username)
        and hmac.compare_digest(password, expected_password)
    ):
        raise AuthError("Invalid username or password.", 401)

    secret = os.getenv("SESSION_SECRET", "")
    if not secret:
        raise AuthError("Session secret not configured.", 500)

    ttl_seconds = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
    now = int(time.time())
    expires_at = now + max(ttl_seconds, 60)

    payload = json.dumps({"sub": username, "iat": now, "exp": expires_at}, separators=(",", ":"))
    payload_segment = _urlsafe_b64encode(payload.encode())
    signature = hmac.new(secret.encode("utf-8"), payload_segment.encode("utf-8"), hashlib.sha256).hexdigest()
    token = f"{payload_segment}.{signature}"
    return token, expires_at


def _urlsafe_b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _response(status: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

