"""Bounded HTTP requests shared by the LinkedIn importer and token renewal."""

import time

import requests


def request(method, url, *, retry_unauthorized=False, **kwargs):
    unauthorized_retries = 0
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
            retryable = status in (429, 500, 502, 503, 504) or (status == 401 and retry_unauthorized)
            if not retryable or attempt == 2:
                raise RuntimeError(f'{method} request failed (HTTP {status})')
            if status == 401:
                delay = (15, 45)[unauthorized_retries]
                unauthorized_retries += 1
                print(f'New LinkedIn access token rejected (HTTP 401); retrying with the same token in {delay} seconds.', flush=True)
            else:
                try:
                    delay = max(delay, min(int(retry_after), 60))
                except ValueError:
                    pass
        time.sleep(delay)
