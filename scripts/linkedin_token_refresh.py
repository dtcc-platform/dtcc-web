#!/usr/bin/env python3
"""Refresh LinkedIn access token using a refresh token.

The importer calls refresh_token() before each fetch and keeps the access
token in memory. Running this script directly checks that renewal works;
neither mode prints tokens or requires copying an access token into secrets.

Required environment variables:
- LINKEDIN_REFRESH_TOKEN: Your refresh token (lasts 1 year)
- LINKEDIN_CLIENT_ID: LinkedIn app client ID
- LINKEDIN_CLIENT_SECRET: LinkedIn app client secret
"""

from __future__ import annotations

import os
import sys

from linkedin_http import request

TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


def refresh_token(*, retry=True) -> str:
    refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN")
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")

    missing = []
    if not refresh_token:
        missing.append("LINKEDIN_REFRESH_TOKEN")
    if not client_id:
        missing.append("LINKEDIN_CLIENT_ID")
    if not client_secret:
        missing.append("LINKEDIN_CLIENT_SECRET")

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    response = request(
        "POST",
        TOKEN_URL,
        retry=retry,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    data = response.json()

    if not isinstance(data, dict):
        raise RuntimeError("Invalid token response: expected an object")
    access_token = data.get("access_token")
    if not isinstance(access_token, str) or not access_token.strip():
        raise RuntimeError("Token response did not contain a valid access token")
    expires_in = data.get("expires_in")
    if type(expires_in) is not int or expires_in <= 0:
        raise RuntimeError("Token response did not contain a valid expiry")

    # GitHub stores the reusable refresh token, not each short-lived access token.
    # A changed grant needs a secure secret update, never a token printed in CI.
    if data.get("refresh_token", refresh_token) != refresh_token:
        raise RuntimeError("LinkedIn returned a replacement refresh token. Reauthorize locally and update LINKEDIN_REFRESH_TOKEN in GitHub secrets.")

    print(f"LinkedIn access token renewed successfully; expires in {expires_in // 86400} days.")
    return access_token


def main() -> int:
    try:
        refresh_token()
        return 0
    except (RuntimeError, ValueError) as exc:
        print(f"LinkedIn token renewal failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
