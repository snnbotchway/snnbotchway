#!/usr/bin/env bash
# Weekly refresh, run from its own clone of main (the service's ExecStartPre syncs it), so it never
# commits to a branch someone is working on. Commits use an identity no GitHub account owns, so they
# add nothing to the contribution graph.
set -euo pipefail

cd "$(dirname "$0")/.."
python3 -I stats/collect.py
python3 -I stats/render.py

git add stats/stats.json assets README.md
if git diff --cached --quiet; then
  exit 0
fi
git -c user.name="Profile stats" -c user.email="profile-stats@snnbotchway.invalid" \
  commit --quiet -m "Refresh shipping stats"
git push --quiet origin HEAD:main
