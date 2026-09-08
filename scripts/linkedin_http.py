"""Bounded HTTP requests shared by the LinkedIn importer and token renewal."""

import time

import requests


def request(method, url, **kwargs):
    for attempt in range(3):
        delay = 2 ** attempt
        try:
            response = requests.request(method, url, timeout=(5, 30), **kwargs)
        except requests.RequestException as exc:
            if attempt == 2 or not isinstance(exc, (requests.Timeout, requests.ConnectionError)):
                # Exception messages and response bodies can contain credentials.
                raise RuntimeError(f'{method} request failed ({type(exc).__name__})') from None
        else:
            if 200 <= response.status_code < 300:
                return response
            status = response.status_code
            retry_after = response.headers.get('Retry-After', '')
            response.close()
            if status not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f'{method} request failed (HTTP {status})')
            try:
                delay = max(delay, min(int(retry_after), 60))
            except ValueError:
                pass
        time.sleep(delay)
