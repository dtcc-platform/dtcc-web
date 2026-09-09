import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import traceback
import unittest
from unittest.mock import patch

import requests


SCRIPTS = Path(__file__).resolve().parents[1]
FEED = Path('public/content/social/linkedin_posts_complete.json')
CREDENTIALS = {
    'LINKEDIN_CLIENT_ID': 'test-client',
    'LINKEDIN_CLIENT_SECRET': 'private-client-secret',
    'LINKEDIN_REFRESH_TOKEN': 'private-refresh-token',
    'LINKEDIN_ACCESS_TOKEN': 'expired-access-token',
}
TOKEN = {
    'access_token': 'private-fresh-access-token',
    'expires_in': 5184000,
    'refresh_token': CREDENTIALS['LINKEDIN_REFRESH_TOKEN'],
    'refresh_token_expires_in': 8640000,
}
POST = {
    'id': 'urn:li:share:2',
    'author': 'urn:li:organization:100491988',
    'commentary': 'A new announcement',
    'createdAt': 2000,
    'publishedAt': 2000,
    'lifecycleState': 'PUBLISHED',
    'visibility': 'PUBLIC',
    'content': {},
}
OLD_FEED = {
    'organization_id': '100491988',
    'total_posts': 1,
    'posts_with_media': 0,
    'posts_with_images': 0,
    'posts': [{
        'post_id': 'urn:li:share:1',
        'post_url': 'https://www.linkedin.com/feed/update/urn:li:share:1/',
        'published_at': 1000,
        'commentary': 'An older announcement',
        'media': {'has_media': False, 'image_url': None},
    }],
}


def response(status, payload, headers=None):
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(payload).encode()
    result._content_consumed = True
    result.headers.update(headers or {})
    result.url = 'https://api.linkedin.com/rest/posts'
    return result


class LinkedInImportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        previous_cwd = Path.cwd()
        os.chdir(self.directory.name)
        self.addCleanup(os.chdir, previous_cwd)
        sys.path.insert(0, str(SCRIPTS))
        self.addCleanup(sys.path.remove, str(SCRIPTS))
        FEED.parent.mkdir(parents=True)
        self.original = json.dumps(OLD_FEED).encode()
        FEED.write_bytes(self.original)
        FEED.chmod(0o640)
        self.calls = []
        self.posts_responses = [response(200, {'elements': [POST]})]
        self.token_responses = [response(200, TOKEN)]
        self.media_responses = {}
        self.output = io.StringIO()
        self.environment = patch.dict(os.environ, CREDENTIALS, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def route_request(self, session, method, url, **kwargs):
        self.calls.append((method.upper(), url, kwargs))
        if url == 'https://www.linkedin.com/oauth/v2/accessToken':
            item = self.token_responses[0]
            if len(self.token_responses) > 1:
                self.token_responses.pop(0)
            return item
        if url == 'https://api.linkedin.com/rest/posts':
            item = self.posts_responses[0]
            if len(self.posts_responses) > 1:
                self.posts_responses.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        if url in self.media_responses:
            return self.media_responses[url]
        raise AssertionError(f'Unexpected request: {method} {url}')

    def run_script(self, name='linkedin_scrape.py'):
        with patch.object(requests.Session, 'request', autospec=True, side_effect=self.route_request), \
                patch('time.sleep') as sleep, \
                contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.output):
            try:
                runpy.run_path(str(SCRIPTS / name), run_name='__main__')
            except SystemExit as exc:
                return exc.code, sleep.call_args_list
            except Exception:
                traceback.print_exc(file=self.output)
                return 1, sleep.call_args_list
        return 0, sleep.call_args_list

    def assert_secrets_hidden(self):
        for secret in [*CREDENTIALS.values(), TOKEN['access_token']]:
            self.assertNotIn(secret, self.output.getvalue())

    def test_authentication_failure_fails_job_and_preserves_feed(self):
        for status, attempts, delays in [(401, 3, [15, 45]), (403, 1, [])]:
            with self.subTest(status=status):
                self.calls.clear()
                self.posts_responses = [response(status, {'message': 'Unauthorized'})]
                code, sleeps = self.run_script()
                self.assertNotEqual(code, 0)
                self.assertEqual(FEED.read_bytes(), self.original)
                self.assertEqual(sum('/rest/posts' in url for _, url, _ in self.calls), attempts)
                self.assertEqual([call.args[0] for call in sleeps], delays)
                self.assertEqual(sum(method == 'POST' for method, _, _ in self.calls), 1)

    def test_fresh_token_rejection_recovers_without_renewing_again(self):
        self.posts_responses.insert(0, response(401, {
            'code': 'REVOKED_ACCESS_TOKEN', 'serviceErrorCode': 65601, 'message': TOKEN,
        }))
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(FEED.read_text())['total_posts'], 2)
        self.assertEqual([call.args[0] for call in sleeps], [15])
        self.assertEqual([method for method, _, _ in self.calls], ['POST', 'GET', 'GET'])
        self.assertTrue(all(kwargs['headers']['Authorization'] == 'Bearer private-fresh-access-token'
                            for _, _, kwargs in self.calls[1:]))
        self.assertIn('HTTP 401', self.output.getvalue())
        self.assert_secrets_hidden()

    def test_fresh_token_rejection_can_recover_on_final_attempt(self):
        self.posts_responses = [response(401, {}), response(401, {}),
                                response(200, {'elements': [POST]})]
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(FEED.read_text())['total_posts'], 2)
        self.assertEqual([call.args[0] for call in sleeps], [15, 45])
        self.assertEqual([method for method, _, _ in self.calls], ['POST', 'GET', 'GET', 'GET'])
        self.assertTrue(all(kwargs['headers']['Authorization'] == 'Bearer private-fresh-access-token'
                            for _, _, kwargs in self.calls[1:]))
        self.assert_secrets_hidden()

    def test_mixed_auth_and_transient_errors_share_attempt_limit(self):
        self.posts_responses = [response(status, {}) for status in [401, 503, 401]]
        self.posts_responses.append(response(200, {'elements': [POST]}))
        code, sleeps = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(FEED.read_bytes(), self.original)
        self.assertEqual([method for method, _, _ in self.calls], ['POST', 'GET', 'GET', 'GET'])
        self.assertEqual([call.args[0] for call in sleeps], [15, 2])

    def test_first_auth_retry_waits_fifteen_seconds_after_a_server_error(self):
        self.posts_responses = [response(503, {}), response(401, {}),
                                response(200, {'elements': [POST]})]
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(FEED.read_text())['total_posts'], 2)
        self.assertEqual([call.args[0] for call in sleeps], [1, 15])
        self.assertEqual([method for method, _, _ in self.calls], ['POST', 'GET', 'GET', 'GET'])

    def test_media_authentication_failure_is_not_retried(self):
        self.posts_responses = [response(200, {'elements': [{**POST, 'content': {'media': {'id': 'urn:li:image:fixture'}}}]})]
        self.media_responses = {
            'https://api.linkedin.com/rest/images/urn%3Ali%3Aimage%3Afixture': response(401, {'message': TOKEN}),
        }
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(FEED.read_text())['posts_with_images'], 0)
        self.assertEqual(sum('/rest/images/' in url for _, url, _ in self.calls), 1)
        self.assertEqual(sleeps, [])
        self.assert_secrets_hidden()

    def test_image_download_authentication_failure_is_not_retried(self):
        image_url = 'https://images.example.test/post.png'
        self.posts_responses = [response(200, {'elements': [{**POST, 'content': {'media': {'id': 'urn:li:image:fixture'}}}]})]
        self.media_responses = {
            'https://api.linkedin.com/rest/images/urn%3Ali%3Aimage%3Afixture': response(200, {'downloadUrl': image_url}),
            image_url: response(401, {'message': TOKEN}),
        }
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        data = json.loads(FEED.read_text())
        self.assertEqual(data['total_posts'], 2)
        self.assertEqual(data['posts'][0]['media']['image_url'], image_url)
        self.assertNotIn('local_image_path', data['posts'][0]['media'])
        download_calls = [kwargs for _, url, kwargs in self.calls if url == image_url]
        self.assertEqual(len(download_calls), 1)
        self.assertNotIn('Authorization', download_calls[0].get('headers', {}))
        self.assertEqual(sleeps, [])
        self.assert_secrets_hidden()

    def test_reshare_parent_authentication_failure_is_not_retried(self):
        parent_url = 'https://api.linkedin.com/rest/posts/urn%3Ali%3Ashare%3A3'
        self.posts_responses = [response(200, {'elements': [{**POST, 'reshareContext': {
            'parent': 'urn:li:share:3', 'root': 'urn:li:share:3',
        }}]})]
        self.media_responses = {parent_url: response(401, {'message': TOKEN})}
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        data = json.loads(FEED.read_text())
        self.assertEqual(data['total_posts'], 2)
        self.assertEqual(data['posts'][0]['reshare_parent_id'], 'urn:li:share:3')
        self.assertIsNone(data['posts'][0]['media']['image_url'])
        self.assertEqual(sum(url == parent_url for _, url, _ in self.calls), 1)
        self.assertEqual(sleeps, [])
        self.assert_secrets_hidden()

    def test_transient_failure_is_retried_then_imports_and_preserves_history(self):
        self.posts_responses.insert(0, response(503, {'message': 'Unavailable'}))
        code, _ = self.run_script()
        self.assertEqual(code, 0)
        data = json.loads(FEED.read_text())
        self.assertEqual([post['post_id'] for post in data['posts']], ['urn:li:share:2', 'urn:li:share:1'])
        self.assertEqual(data['total_posts'], 2)
        self.assertEqual(data['posts'][0]['commentary'], 'A new announcement')
        self.assertEqual(FEED.stat().st_mode & 0o777, 0o640)

    def test_exhausted_transient_errors_fail_after_bounded_attempts(self):
        self.posts_responses = [response(503, {'message': 'Unavailable'})]
        code, _ = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(sum('/rest/posts' in url for _, url, _ in self.calls), 3)
        self.assertEqual(FEED.read_bytes(), self.original)

    def test_connection_error_and_timeout_are_retried(self):
        for error in [requests.ConnectionError('disconnected'), requests.Timeout('timed out')]:
            with self.subTest(error=type(error).__name__):
                self.posts_responses = [error, response(200, {'elements': [POST]})]
                code, _ = self.run_script()
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(FEED.read_text())['total_posts'], 2)

    def test_rate_limit_wait_is_bounded(self):
        self.posts_responses.insert(0, response(429, {}, {'Retry-After': '86400'}))
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        self.assertTrue(sleeps)
        self.assertTrue(all(0 < call.args[0] <= 60 for call in sleeps))
        self.assertEqual(json.loads(FEED.read_text())['total_posts'], 2)

    def test_malformed_success_response_fails_without_changing_feed(self):
        for payload in [{}, [], {'elements': {}}, {'elements': [None]}, {'elements': [{'id': 'missing-date'}]}]:
            with self.subTest(payload=payload):
                self.posts_responses = [response(200, payload)]
                code, _ = self.run_script()
                self.assertNotEqual(code, 0)
                self.assertEqual(FEED.read_bytes(), self.original)

    def test_invalid_json_fails_without_changing_feed(self):
        self.posts_responses[0]._content = b'<html>Upstream error</html>'
        code, _ = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(FEED.read_bytes(), self.original)

    def test_non_text_commentary_fails_without_changing_feed(self):
        for commentary in [{'text': 'Wrong shape'}, ['Wrong shape'], 123, None]:
            with self.subTest(commentary=commentary):
                self.posts_responses = [response(200, {'elements': [{**POST, 'commentary': commentary}]})]
                code, _ = self.run_script()
                self.assertNotEqual(code, 0)
                self.assertEqual(FEED.read_bytes(), self.original)

    def test_downloaded_image_is_saved_and_linked_using_fresh_api_credentials(self):
        self.posts_responses = [response(200, {'elements': [{**POST, 'content': {'media': {'id': 'urn:li:image:fixture'}}}]})]
        image_response = response(200, {}, {'Content-Type': 'image/png'})
        image_response._content = b'fixture image bytes'
        self.media_responses = {
            'https://api.linkedin.com/rest/images/urn%3Ali%3Aimage%3Afixture': response(200, {'downloadUrl': 'https://images.example.test/post.png'}),
            'https://images.example.test/post.png': image_response,
        }
        code, _ = self.run_script()
        self.assertEqual(code, 0)
        data = json.loads(FEED.read_text())
        self.assertEqual(data['posts_with_images'], 1)
        image = Path('public') / data['posts'][0]['media']['image_url']
        self.assertEqual(image.read_bytes(), b'fixture image bytes')
        for _, url, kwargs in self.calls:
            if '/rest/images/' in url:
                self.assertEqual(kwargs['headers']['Authorization'], 'Bearer private-fresh-access-token')
                self.assertIn('timeout', kwargs)
            if url.startswith('https://images.example.test/'):
                self.assertNotIn('Authorization', kwargs.get('headers', {}))
        self.assert_secrets_hidden()

    def test_invalid_existing_feed_is_not_silently_discarded(self):
        FEED.write_bytes(b'{broken')
        code, _ = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(FEED.read_bytes(), b'{broken')

    def test_failed_atomic_replacement_preserves_feed_and_removes_temporary_file(self):
        with patch('os.replace', side_effect=OSError('Disk write failure')):
            code, _ = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(FEED.read_bytes(), self.original)
        self.assertEqual(list(FEED.parent.glob('.*.tmp')), [])

    def test_refreshes_before_fetch_and_uses_fresh_token_with_timeouts(self):
        code, sleeps = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(sleeps, [])
        method, url, kwargs = self.calls[0]
        self.assertEqual((method, url), ('POST', 'https://www.linkedin.com/oauth/v2/accessToken'))
        self.assertEqual(kwargs['data']['grant_type'], 'refresh_token')
        self.assertEqual(kwargs['data']['refresh_token'], CREDENTIALS['LINKEDIN_REFRESH_TOKEN'])
        self.assertEqual(self.calls[1][2]['headers']['Authorization'], 'Bearer private-fresh-access-token')
        for _, _, kwargs in self.calls:
            connect, read = kwargs['timeout']
            self.assertGreater(connect, 0)
            self.assertGreater(read, 0)
        self.assert_secrets_hidden()

    def test_failed_refresh_stops_before_fetch_and_does_not_log_response_secrets(self):
        for status in [400, 401]:
            with self.subTest(status=status):
                self.calls.clear()
                self.token_responses = [response(status, {'error': 'invalid_grant', 'echo': TOKEN})]
                code, sleeps = self.run_script()
                self.assertNotEqual(code, 0)
                self.assertEqual(len(self.calls), 1)
                self.assertEqual(sleeps, [])
                self.assertEqual(FEED.read_bytes(), self.original)
                self.assert_secrets_hidden()

    def test_missing_refresh_credentials_fails_before_any_request(self):
        os.environ.pop('LINKEDIN_REFRESH_TOKEN')
        code, _ = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(FEED.read_bytes(), self.original)

    def test_invalid_token_response_fails_without_logging_tokens(self):
        for payload in [[], {'refresh_token': 'private-refresh-token'}, {**TOKEN, 'access_token': ''}, {**TOKEN, 'expires_in': 0}]:
            with self.subTest(payload=payload):
                self.token_responses = [response(200, payload)]
                code, _ = self.run_script('linkedin_token_refresh.py')
                self.assertNotEqual(code, 0)
                self.assert_secrets_hidden()

    def test_manual_refresh_checks_credentials_without_printing_tokens(self):
        code, _ = self.run_script('linkedin_token_refresh.py')
        self.assertEqual(code, 0)
        self.assert_secrets_hidden()

    def test_token_endpoint_transient_failure_is_retried_before_import(self):
        self.token_responses.insert(0, response(503, {'message': 'Unavailable'}))
        code, _ = self.run_script()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(FEED.read_text())['total_posts'], 2)
        self.assert_secrets_hidden()

    def test_replacement_refresh_token_requires_secure_reauthorization(self):
        self.token_responses = [response(200, {**TOKEN, 'refresh_token': 'private-replacement-token'})]
        code, _ = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(FEED.read_bytes(), self.original)
        self.assertNotIn('private-replacement-token', self.output.getvalue())
        self.assert_secrets_hidden()


if __name__ == '__main__':
    unittest.main()
