#!/usr/bin/env bash
# Rebuild publications.html from the latest agentic-frontier and push if it changed.
# Runs on the Hostkey VPS (systemd timer adanman-site-refresh.timer, hourly) so the
# site catches up within the hour after the agentic-frontier routine writes a post.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
AF_DIR="${AF_DIR:-/opt/agentic-frontier}"
cd "$AF_DIR" && git pull -q --ff-only origin main
cd "$REPO" && git pull -q --ff-only origin main
AF_DIR="$AF_DIR" python3 scripts/build_site.py >/dev/null
if [ -n "$(git status --porcelain publications.html)" ]; then
  git add publications.html
  git commit -q -m "site: refresh $(date -u +%Y-%m-%d)" \
    --author="Danila Katalshov <56929384+ADanMan@users.noreply.github.com>"
  git push -q origin main
  echo "$(date -u) pushed publications.html"
else
  echo "$(date -u) no new publications"
fi
