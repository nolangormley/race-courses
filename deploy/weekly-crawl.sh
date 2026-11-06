#!/usr/bin/env bash
# Crawl every race and push what changed. race-courses-crawl.service runs it in a checkout that it
# first resets to origin/main, so the checkout holds no work of its own.
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync --locked --quiet
uv run race-courses crawl
git add -A
if ! git diff --cached --quiet; then
    git commit --quiet -m "Weekly crawl $(date -u +%Y-%m-%d)"
    git push --quiet origin HEAD:main
fi
