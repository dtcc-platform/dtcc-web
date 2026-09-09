import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import requests


SCRIPTS = Path(__file__).resolve().parents[1]
CREDENTIALS = {
    'LINKEDIN_CLIENT_ID': 'fixture-client',
    'LINKEDIN_CLIENT_SECRET': 'fixture-secret',
    'LINKEDIN_REFRESH_TOKEN': 'fixture-refresh-token',
    'LINKEDIN_ACCESS_TOKEN': 'fixture-expired-token',
}
ACCESS_TOKEN = 'fixture-fresh-token'
ACCEPTED = (200, {'elements': [{}, {}]})
REJECTED = (401, {'code': 'INVALID_ACCESS_TOKEN', 'serviceErrorCode': 65600})


class LinkedInDiagnosticTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        previous_cwd = Path.cwd()
        os.chdir(directory.name)
        self.addCleanup(os.chdir, previous_cwd)
        self.feed = Path('existing-feed.json')
        self.feed.write_bytes(b'unchanged feed')
        sys.path.insert(0, str(SCRIPTS))
        self.addCleanup(sys.path.remove, str(SCRIPTS))
        self.elapsed = 0
        self.calls = []
        self.output = io.StringIO()
        self.posts = [ACCEPTED, ACCEPTED, ACCEPTED]
        self.token = (200, {
            'access_token': ACCESS_TOKEN,
            'expires_in': 5184000,
            'refresh_token': CREDENTIALS['LINKEDIN_REFRESH_TOKEN'],
        })

    def sleep(self, seconds):
        self.assertGreaterEqual(seconds, 0)
        self.elapsed += seconds

    def transport(self, adapter, prepared, **kwargs):
        self.calls.append(prepared)
        self.assertEqual(kwargs['timeout'], (5, 30))
        if prepared.url == 'https://www.linkedin.com/oauth/v2/accessToken':
            item = self.token
        else:
            self.assertEqual(urlparse(prepared.url).netloc, 'api.linkedin.com')
            self.assertEqual(urlparse(prepared.url).path, '/rest/posts')
            item = self.posts.pop(0)
        if isinstance(item, Exception):
            raise item
        status, payload = item
        response = requests.Response()
        response.status_code = status
        response.request = prepared
        response.url = prepared.url
        response._content = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        response._content_consumed = True
        if status == 302:
            response.headers['Location'] = f'https://other.example/{ACCESS_TOKEN}'
        return response

    def run_script(self):
        with patch.dict(os.environ, CREDENTIALS, clear=True), \
                patch.object(requests.adapters.HTTPAdapter, 'send', autospec=True, side_effect=self.transport), \
                patch('time.monotonic', side_effect=lambda: self.elapsed), \
                patch('time.sleep', side_effect=self.sleep), \
                contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.output):
            try:
                runpy.run_path(str(SCRIPTS / 'linkedin_diagnose.py'), run_name='__main__')
            except SystemExit as exc:
                code = exc.code
            except Exception as exc:
                self.output.write(f'Unexpected failure: {type(exc).__name__}\n')
                code = 1
            else:
                code = 0
        reports = [json.loads(line) for line in self.output.getvalue().splitlines() if line.startswith('{')]
        for secret in [*CREDENTIALS.values(), ACCESS_TOKEN]:
            self.assertNotIn(secret, self.output.getvalue())
        self.assertEqual(self.feed.read_bytes(), b'unchanged feed')
        self.assertEqual(list(Path('.').iterdir()), [self.feed])
        return code, reports

    def test_delayed_acceptance_reuses_one_token_at_three_times_without_writing_feed(self):
        self.posts = [REJECTED, ACCEPTED, ACCEPTED]
        code, reports = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual([report['http_status'] for report in reports], [401, 200, 200])
        self.assertEqual([report['elapsed_seconds'] for report in reports], [0, 15, 60])
        self.assertEqual([request.method for request in self.calls], ['POST', 'GET', 'GET', 'GET'])
        self.assertEqual(parse_qs(self.calls[0].body)['grant_type'], ['refresh_token'])
        for request in self.calls[1:]:
            self.assertEqual(request.headers['Authorization'], 'Bearer fixture-fresh-token')
            self.assertEqual(request.headers['LinkedIn-Version'], '202601')
            self.assertEqual(request.headers['X-Restli-Protocol-Version'], '2.0.0')
            self.assertEqual(parse_qs(urlparse(request.url).query)['author'], ['urn:li:organization:100491988'])
        self.assertTrue(all(report['bearer_header_preserved'] for report in reports))
        self.assertEqual(reports[-1]['post_count'], 2)

    def test_persistent_rejection_fails_and_reports_only_safe_error_fields(self):
        self.posts = [(401, {**REJECTED[1], 'message': ACCESS_TOKEN, 'debug': CREDENTIALS})] * 3
        code, reports = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(len(reports), 3)
        self.assertTrue(all(report['code'] == 'INVALID_ACCESS_TOKEN' for report in reports))
        self.assertTrue(all(report['serviceErrorCode'] == 65600 for report in reports))
        self.assertTrue(all('message' not in report and 'debug' not in report for report in reports))

    def test_unrecognized_error_fields_and_non_json_bodies_do_not_leak(self):
        self.posts = [(401, {'code': ACCESS_TOKEN, 'serviceErrorCode': ACCESS_TOKEN}),
                      (401, ACCESS_TOKEN.encode()), (401, [ACCESS_TOKEN])]
        code, reports = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual([report['http_status'] for report in reports], [401, 401, 401])
        self.assertEqual(reports[0]['code'], 'unrecognized')
        self.assertNotIn('serviceErrorCode', reports[0])

    def test_transport_error_is_sanitized_and_later_probes_still_run(self):
        self.posts = [requests.ConnectionError(ACCESS_TOKEN), ACCEPTED, ACCEPTED]
        code, reports = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(reports[0]['error_type'], 'ConnectionError')
        self.assertEqual(reports[-1]['elapsed_seconds'], 60)
        self.assertEqual(len(self.calls), 4)

    def test_failed_renewal_sends_no_posts_requests(self):
        self.token = (400, {'message': ACCESS_TOKEN, 'debug': CREDENTIALS})
        code, reports = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual([request.method for request in self.calls], ['POST'])
        self.assertEqual(reports[0]['stage'], 'token_renewal')

    def test_renewal_read_timeout_is_not_retried(self):
        self.token = requests.ReadTimeout(ACCESS_TOKEN)
        code, reports = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual([request.method for request in self.calls], ['POST'])
        self.assertEqual(reports[0]['stage'], 'token_renewal')

    def test_renewal_transient_http_error_is_not_retried(self):
        self.token = (503, {'message': ACCESS_TOKEN})
        code, reports = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual([request.method for request in self.calls], ['POST'])
        self.assertEqual(reports[0]['stage'], 'token_renewal')

    def test_redirects_are_reported_without_following_or_printing_the_destination(self):
        self.posts = [(302, {})] * 3
        code, reports = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(len(self.calls), 4)
        self.assertEqual([report['http_status'] for report in reports], [302, 302, 302])
        self.assertTrue(all(report['redirect'] for report in reports))

    def test_malformed_success_is_not_reported_as_working_posts_access(self):
        self.posts = [(200, {}), (200, []), (200, {'elements': ACCESS_TOKEN})]
        code, reports = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual([report['http_status'] for report in reports], [200, 200, 200])
        self.assertTrue(all('post_count' not in report for report in reports))


if __name__ == '__main__':
    unittest.main()
