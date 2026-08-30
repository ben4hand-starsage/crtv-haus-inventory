#!/usr/bin/env bash
# Sync DELAY/site -> the deploy repo, then commit and push.
#
# This exists so the excludes can't be forgotten. The deploy repo holds two
# things that do NOT come from DELAY/site and that a bare `rsync --delete`
# would silently destroy:
#
#   .github/                 the workflow that refreshes the analytics snapshot
#   pulse-8f3ac2/data.json   written by that workflow, not by us
#
# Usage:  tools/sync_site.sh "commit message"
set -euo pipefail

SRC="/Users/benjaminforehand/Desktop/CLAUDE/DELAY/site"
DST="/Users/benjaminforehand/Desktop/aarondelaycounseling-site"
TOOL="/Users/benjaminforehand/Desktop/CLAUDE/tools/fetch_cloudflare_analytics.py"
MSG="${1:-Sync site}"

[ -d "$SRC" ] || { echo "missing source: $SRC" >&2; exit 1; }
[ -d "$DST/.git" ] || { echo "not a git repo: $DST" >&2; exit 1; }

rsync -a --delete \
  --exclude '.git' \
  --exclude '.github' \
  --exclude '.DS_Store' \
  --exclude 'pulse-8f3ac2/data.json' \
  "$SRC"/ "$DST"/

# The workflow's copy of the fetcher is generated from the canonical tool, so
# the two can never drift.
mkdir -p "$DST/.github/scripts"
cp "$TOOL" "$DST/.github/scripts/fetch_analytics.py"

cd "$DST"
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "  nothing changed"
  exit 0
fi
git add -A
git status --short | sed 's/^/  /'
git commit -q -m "$MSG"
git push -q origin main
echo "  pushed: $(git rev-parse --short HEAD)"
