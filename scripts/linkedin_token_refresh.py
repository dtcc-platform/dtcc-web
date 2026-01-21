#!/usr/bin/env python3
"""Refresh LinkedIn access token using a refresh token.

This script is designed to run in GitHub Actions. It uses the refresh token
to obtain a new access token and prints it for manual copying to the
LINKEDIN_ACCESS_TOKEN secret.

Required environment variables:
- LINKEDIN_REFRESH_TOKEN: Your refresh token (lasts 1 year)
- LINKEDIN_CLIENT_ID: LinkedIn app client ID
- LINKEDIN_CLIENT_SECRET: LinkedIn app client secret
"""

from __future__ import annotations

import os
import sys

import requests

TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


def refresh_token() -> int:
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
        print(f"Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        return 1

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )

    if response.status_code != 200:
        print(f"Token refresh failed with status {response.status_code}: {response.text}", file=sys.stderr)
        return 2

    data = response.json()

    access_token = data.get("access_token")
    if not access_token:
        print(f"Response did not contain access_token: {data}", file=sys.stderr)
        return 3

    expires_in = data.get("expires_in", 0)
    expires_in_days = expires_in // 86400

    print("=" * 60)
    print("NEW ACCESS TOKEN (copy this to LINKEDIN_ACCESS_TOKEN secret):")
    print("=" * 60)
    print(access_token)
    print("=" * 60)
    print(f"Expires in: {expires_in_days} days ({expires_in} seconds)")

    if "refresh_token" in data:
        print()
        print("New refresh token also returned (update LINKEDIN_REFRESH_TOKEN if different):")
        print(data["refresh_token"])

    return 0


if __name__ == "__main__":
    sys.exit(refresh_token())
