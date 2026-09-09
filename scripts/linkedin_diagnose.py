"""Compare immediate and delayed posts access using one freshly renewed token."""

import json
import sys
import time

import requests

from linkedin_scrape import ORGANIZATION_ID, POSTS_API_BASE
from linkedin_token_refresh import refresh_token


SAFE_ERROR_CODES = {
    'EMPTY_ACCESS_TOKEN', 'INVALID_ACCESS_TOKEN', 'EXPIRED_ACCESS_TOKEN',
    'REVOKED_ACCESS_TOKEN', 'ACCESS_DENIED', 'UNAUTHORIZED', 'FORBIDDEN',
}


def probe_posts(access_token):
    with requests.get(
        POSTS_API_BASE,
        headers={
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202601',
        },
        params={'author': f'urn:li:organization:{ORGANIZATION_ID}',
                'q': 'author', 'count': 20, 'sortBy': 'CREATED'},
        timeout=(5, 30),
        allow_redirects=False,
    ) as response:
        result = {
            'http_status': response.status_code,
            'bearer_header_preserved': response.request.headers.get('Authorization') == f'Bearer {access_token}',
            'redirect': response.is_redirect,
        }
        try:
            data = response.json()
        except ValueError:
            result['response_format'] = 'non_json'
            return result
        if not isinstance(data, dict):
            result['response_format'] = 'non_object'
            return result
        if response.status_code == 200 and isinstance(data.get('elements'), list):
            result['post_count'] = len(data['elements'])
        # Only recognized codes and numeric subcodes leave this process.
        # Raw messages, response bodies and header values can contain secrets.
        if 'code' in data:
            code = data['code']
            result['code'] = code if isinstance(code, str) and code in SAFE_ERROR_CODES else 'unrecognized'
        subcode = data.get('serviceErrorCode')
        if type(subcode) is int and 0 <= subcode <= 2147483647:
            result['serviceErrorCode'] = subcode
        return result


def main():
    try:
        access_token = refresh_token(retry=False)
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({'stage': 'token_renewal', 'error_type': type(exc).__name__}), flush=True)
        return 1

    started = time.monotonic()
    for offset in (0, 15, 60):
        time.sleep(max(0, offset - (time.monotonic() - started)))
        result = {'elapsed_seconds': round(time.monotonic() - started, 3)}
        try:
            result.update(probe_posts(access_token))
        except requests.RequestException as exc:
            result['error_type'] = type(exc).__name__
        print(json.dumps(result), flush=True)
    return 0 if 'post_count' in result else 1


if __name__ == '__main__':
    sys.exit(main())
