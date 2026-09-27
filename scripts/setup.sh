#!/usr/bin/env bash
# Install WordPress (first run) and (re)load all site pages from content/.
# Safe to re-run: existing pages are updated in place, matched by slug.
# Usage: scripts/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
POD=srcmsr
PORT="${PORT:-8092}"

python3 "$ROOT/tools/build_content.py"

# Wait for WordPress files and the database.
for i in $(seq 1 60); do
	if podman exec "$POD-cli" test -f /var/www/html/wp-config.php 2>/dev/null &&
		podman exec "$POD-cli" wp db check --quiet >/dev/null 2>&1; then
		break
	fi
	[ "$i" = 60 ] && { echo "WordPress/DB not ready. Is the pod running? (scripts/start.sh)"; exit 1; }
	sleep 2
done

podman exec -e SITE_URL="http://localhost:$PORT" "$POD-cli" bash /project/scripts/setup-inside.sh
