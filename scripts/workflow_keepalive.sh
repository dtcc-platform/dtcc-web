#!/usr/bin/env bash
set -euo pipefail

branch="${GITHUB_REF_NAME:?GITHUB_REF_NAME must name the default branch}"
git fetch --no-tags origin "refs/heads/$branch"
base=$(git rev-parse FETCH_HEAD)
last_commit=$(git show -s --format=%ct "$base")
age=$(( ($(date +%s) - last_commit) / 86400 ))

if [ "$age" -lt 50 ]; then
  echo "Latest commit is $age days old; no keepalive needed."
  exit 0
fi

# Start from the current remote branch, even if this run waited in a queue.
git checkout --detach "$base"
mkdir -p .github
date -u +%Y-%m-%dT%H:%M:%SZ > .github/keepalive
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add .github/keepalive
git commit -m "Chore: Recorded workflow keepalive"

if git push origin "HEAD:refs/heads/$branch"; then
  echo "Published keepalive after $age quiet days."
  exit 0
fi

# A human push can still race with us. Accept fresh activity, never force-push.
git fetch --no-tags origin "refs/heads/$branch"
current=$(git rev-parse FETCH_HEAD)
last_commit=$(git show -s --format=%ct "$current")
age=$(( ($(date +%s) - last_commit) / 86400 ))
if [ "$current" != "$base" ] && [ "$age" -lt 50 ]; then
  echo "Another push supplied recent activity; no keepalive needed."
  exit 0
fi

echo "Keepalive push failed; repository activity was not refreshed." >&2
exit 1
