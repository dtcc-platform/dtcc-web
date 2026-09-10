import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'workflow_keepalive.sh'
DAY = 86400


class WorkflowKeepaliveTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.remote = self.root / 'remote.git'
        self.seed = self.root / 'seed'
        self.checkout = self.root / 'checkout'
        self.now = int(time.time())
        self.environment = {
            'PATH': os.environ['PATH'],
            'HOME': str(self.root),
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_TERMINAL_PROMPT': '0',
            'GITHUB_REF_NAME': 'main',
        }
        self.git(self.root, 'init', '--bare', '--initial-branch=main', str(self.remote))
        self.git(self.root, 'init', '--initial-branch=main', str(self.seed))
        self.git(self.seed, 'config', 'user.name', 'Test author')
        self.git(self.seed, 'config', 'user.email', 'test@example.invalid')
        self.git(self.seed, 'remote', 'add', 'origin', str(self.remote))
        (self.seed / 'feed.json').write_text('[]\n')

    def git(self, directory, *args, extra_env=None):
        result = subprocess.run(
            ['git', *args], cwd=directory,
            env={**self.environment, **(extra_env or {})},
            text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, days_old):
        timestamp = f'{self.now - days_old * DAY} +0000'
        self.git(self.seed, 'add', 'feed.json')
        self.git(self.seed, 'commit', '-m', 'Updated feed', extra_env={
            'GIT_AUTHOR_DATE': timestamp, 'GIT_COMMITTER_DATE': timestamp,
        })
        return self.git(self.seed, 'rev-parse', 'HEAD')

    def prepare(self, days_old):
        head = self.commit(days_old)
        self.git(self.seed, 'push', 'origin', 'main')
        self.git(self.root, 'clone', '--depth=1', '--branch=main',
                 self.remote.as_uri(), str(self.checkout))
        return head

    def run_keepalive(self):
        return subprocess.run(
            ['bash', str(SCRIPT)], cwd=self.checkout, env=self.environment,
            text=True, capture_output=True, timeout=10,
        )

    def test_recent_activity_does_not_create_a_commit(self):
        original = self.prepare(49)
        result = self.run_keepalive()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), original)
        self.assertFalse((self.checkout / '.github/keepalive').exists())

    def test_fifty_quiet_days_creates_only_a_timestamp_commit(self):
        original = self.prepare(50)
        result = self.run_keepalive()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main^'), original)
        self.assertEqual(self.git(self.remote, 'diff', '--name-only', 'main^', 'main'),
                         '.github/keepalive')
        self.assertRegex(self.git(self.remote, 'show', 'main:.github/keepalive'),
                         r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
        self.assertEqual(self.git(self.remote, 'show', '-s', '--format=%an', 'main'),
                         'github-actions[bot]')

    def test_second_run_does_not_repeat_the_keepalive_commit(self):
        self.prepare(70)
        result = self.run_keepalive()
        self.assertEqual(result.returncode, 0, result.stderr)
        head = self.git(self.remote, 'rev-parse', 'main')
        result = self.run_keepalive()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), head)

    def test_stale_checkout_checks_current_remote_activity(self):
        self.prepare(70)
        (self.seed / 'feed.json').write_text('["new post"]\n')
        updated = self.commit(0)
        self.git(self.seed, 'push', 'origin', 'main')
        result = self.run_keepalive()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), updated)

    def test_stale_checkout_builds_keepalive_on_current_remote_commit(self):
        self.prepare(70)
        (self.seed / 'feed.json').write_text('["new post"]\n')
        updated = self.commit(60)
        self.git(self.seed, 'push', 'origin', 'main')
        result = self.run_keepalive()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main^'), updated)
        self.assertEqual(self.git(self.remote, 'show', 'main:feed.json'), '["new post"]')
        self.assertEqual(self.git(self.remote, 'diff', '--name-only', 'main^', 'main'),
                         '.github/keepalive')

    def test_competing_push_preserves_new_activity(self):
        self.prepare(70)
        updated = self.competing_push(0)
        result = self.run_keepalive()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), updated)
        self.assertEqual(self.git(self.remote, 'show', 'main:feed.json'), '["new post"]')
        self.assertNotIn('.github/keepalive', self.git(self.remote, 'ls-tree', '-r', 'main'))

    def test_competing_old_commit_does_not_hide_failed_keepalive(self):
        self.prepare(70)
        updated = self.competing_push(60)
        result = self.run_keepalive()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), updated)

    def competing_push(self, days_old):
        (self.seed / 'feed.json').write_text('["new post"]\n')
        updated = self.commit(days_old)
        hook = self.checkout / '.git/hooks/pre-push'
        hook.write_text('#!/bin/sh\nunset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE\n'
                        f'git -C {shlex.quote(str(self.seed))} push origin main\n')
        hook.chmod(0o755)
        return updated

    def test_rejected_push_fails_and_preserves_remote_history(self):
        original = self.prepare(70)
        hook = self.remote / 'hooks/pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        result = self.run_keepalive()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), original)

    def test_fetch_failure_fails_without_creating_a_commit(self):
        original = self.prepare(70)
        self.git(self.checkout, 'remote', 'set-url', 'origin', str(self.root / 'missing.git'))
        result = self.run_keepalive()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git(self.checkout, 'rev-parse', 'HEAD'), original)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), original)


if __name__ == '__main__':
    unittest.main()
