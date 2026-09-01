#!/usr/bin/env bash
# Manual equivalent of the daily Actions run: fetch, commit, push.
# The snapshot lives only in the deploy repo, so this writes straight there.
set -euo pipefail
DST="/Users/benjaminforehand/Desktop/aarondelaycounseling-site"
cd /Users/benjaminforehand/Desktop/CLAUDE
python3 tools/fetch_cloudflare_analytics.py --days "${1:-30}"
cd "$DST"
if git diff --quiet -- siteanalytics/data.json; then
  echo "  numbers unchanged; nothing to push"
  exit 0
fi
git add siteanalytics/data.json
git commit -q -m "Refresh analytics snapshot"
git push -q origin main
echo "  pushed: $(git rev-parse --short HEAD)"
