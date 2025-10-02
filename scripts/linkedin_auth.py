#!/usr/bin/env python3
"""LinkedIn OAuth helper.

This script performs the Authorization Code flow for LinkedIn's Marketing
Developer Platform. It spins up a temporary local HTTP server, directs you to
LinkedIn's consent screen, captures the returned ``code`` parameter, and
exchanges it for an access token (and optional refresh token).

Prerequisites
-------------
1. Your LinkedIn application must have the **Marketing Developer Platform**
   product enabled.
2. The redirect URI you use here must be registered under your app's *Auth*
   settings (e.g. ``http://localhost:8765/callback``).
3. The account completing the login must be an admin of the organisation you
   plan to query and must grant the ``w_organization_social`` and
   ``r_organization_social`` scopes.

Usage
-----

.. code-block:: bash

   export LINKEDIN_CLIENT_ID="..."
   export LINKEDIN_CLIENT_SECRET="..."
   python3 scripts/linkedin_auth.py --scopes w_organization_social r_organization_social

The script will print the access token JSON response. Copy the ``access_token``
value into ``LINKEDIN_ACCESS_TOKEN`` when running ``linkedin_feed.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Iterable, Optional

import requests


AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


class OAuthParams:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes: Iterable[str]):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = list(scopes)


class CodeReceiver(BaseHTTPRequestHandler):
    """HTTP handler that captures the ``code`` parameter from LinkedIn."""

    server: HTTPServer  # type: ignore[assignment]

    def log_message(self, format: str, *args):  # noqa: D401 - silence default logging
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != self.server.callback_path:
            self.send_error(404)
            return

        params = urllib.parse.parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]

        if not code:
            self.send_error(400, "Missing code parameter")
            self.server.auth_error = "LinkedIn did not return an authorization code."
            return

        if state != self.server.expected_state:
            self.send_error(400, "State mismatch")
            self.server.auth_error = "State parameter mismatch; aborting."
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><body><h2>LinkedIn authorization captured.</h2>"
                         b"<p>You may close this window.</p></body></html>")

        self.server.auth_code = code
        self.server.stop_event.set()


class OAuthServer(HTTPServer):
    def __init__(self, address: tuple[str, int], handler: type[CodeReceiver], expected_state: str, callback_path: str):
        super().__init__(address, handler)
        self.expected_state = expected_state
        self.callback_path = callback_path
        self.auth_code: Optional[str] = None
        self.auth_error: Optional[str] = None
        self.stop_event = threading.Event()


def start_server(port: int, state: str, callback_path: str) -> OAuthServer:
    server = OAuthServer(("127.0.0.1", port), CodeReceiver, state, callback_path)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def build_auth_url(params: OAuthParams, state: str) -> str:
    query = {
        "response_type": "code",
        "client_id": params.client_id,
        "redirect_uri": params.redirect_uri,
        "scope": " ".join(params.scopes),
        "state": state,
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(query)}"


def exchange_code(params: OAuthParams, code: str) -> dict:
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": params.redirect_uri,
        "client_id": params.client_id,
        "client_secret": params.client_secret,
    }
    response = requests.post(TOKEN_URL, data=payload, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(
            f"Token exchange failed with status {response.status_code}: {response.text}"
        )
    return response.json()


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-id", default=os.getenv("LINKEDIN_CLIENT_ID"), help="App client ID")
    parser.add_argument("--client-secret", default=os.getenv("LINKEDIN_CLIENT_SECRET"), help="App client secret")
    parser.add_argument("--redirect-uri", default=os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8765/callback"), help="Registered redirect URI")
    parser.add_argument("--port", type=int, default=8765, help="Local server port")
    parser.add_argument("--callback-path", default="/callback", help="Callback path component (must match redirect URI)")
    parser.add_argument("--scopes", nargs="*", default=["w_organization_social", "r_organization_social"], help="Space-separated scope list")
    parser.add_argument("--no-browser", action="store_true", help="Print the authorization URL instead of opening a browser")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the token response")
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    if not args.client_id or not args.client_secret:
        print("Client ID/secret are required (set env or pass flags).", file=sys.stderr)
        return 1

    params = OAuthParams(args.client_id, args.client_secret, args.redirect_uri, args.scopes)
    state = secrets.token_urlsafe(16)

    server = start_server(args.port, state, args.callback_path)

    auth_url = build_auth_url(params, state)
    print("Open this URL in a browser to authorize the app:\n")
    print(auth_url)

    if not args.no_browser:
        try:
            webbrowser.open(auth_url)
        except Exception:
            print("Failed to open browser automatically; please copy the URL manually.")

    print("\nWaiting for LinkedIn callback (Ctrl+C to abort)...")
    try:
        server.stop_event.wait(timeout=300)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130
    finally:
        server.shutdown()

    if server.auth_error:
        print(f"Authorization failed: {server.auth_error}", file=sys.stderr)
        return 2
    if not server.auth_code:
        print("Did not receive an authorization code within the timeout.", file=sys.stderr)
        return 3

    try:
        token = exchange_code(params, server.auth_code)
    except Exception as exc:
        print(f"Token exchange error: {exc}", file=sys.stderr)
        return 4

    json_kwargs = {"indent": 2, "ensure_ascii": False} if args.pretty else {"separators": (",", ":"), "ensure_ascii": False}
    json.dump(token, sys.stdout, **json_kwargs)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
