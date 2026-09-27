#!/usr/bin/env bash
# Package the site for live hosting: theme zip, database dump, uploads.
# Output: dist/  (see README "Going live")
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/dist"
(cd "$ROOT/wp-content/themes" && zip -qr "$ROOT/dist/shriram-college-theme.zip" shriram-college)
podman exec srcmsr-cli wp db export - > "$ROOT/dist/database.sql"
podman exec srcmsr-cli tar czf - -C /var/www/html/wp-content uploads > "$ROOT/dist/uploads.tar.gz"
echo "Exported to $ROOT/dist:"; ls -lh "$ROOT/dist"
