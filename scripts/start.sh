#!/usr/bin/env bash
# Start the local WordPress stack (MariaDB + WordPress + WP-CLI) in a Podman pod.
# Usage: scripts/start.sh            -> http://localhost:8092
#        PORT=9000 scripts/start.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
POD=srcmsr
PORT="${PORT:-8092}"

if podman pod exists "$POD"; then
	podman pod start "$POD" >/dev/null
	echo "Pod $POD started: http://localhost:$PORT"
	exit 0
fi

podman pod create --name "$POD" -p "$PORT:80" >/dev/null

podman run -d --pod "$POD" --name "$POD-db" \
	-e MARIADB_DATABASE=wordpress -e MARIADB_USER=wp -e MARIADB_PASSWORD=wp -e MARIADB_ROOT_PASSWORD=root \
	-v "$POD-db:/var/lib/mysql" \
	docker.io/library/mariadb:11 >/dev/null

podman run -d --pod "$POD" --name "$POD-wp" \
	-e WORDPRESS_DB_HOST=127.0.0.1 -e WORDPRESS_DB_USER=wp -e WORDPRESS_DB_PASSWORD=wp -e WORDPRESS_DB_NAME=wordpress \
	-v "$POD-html:/var/www/html" \
	-v "$ROOT/wp-content/themes/shriram-college:/var/www/html/wp-content/themes/shriram-college:z" \
	docker.io/library/wordpress:php8.3-apache >/dev/null

# WP-CLI container shares the WordPress files; uid 33 = www-data in the apache image.
podman run -d --pod "$POD" --name "$POD-cli" --user 33:33 \
	-e WORDPRESS_DB_HOST=127.0.0.1 -e WORDPRESS_DB_USER=wp -e WORDPRESS_DB_PASSWORD=wp -e WORDPRESS_DB_NAME=wordpress \
	-v "$POD-html:/var/www/html" \
	-v "$ROOT/wp-content/themes/shriram-college:/var/www/html/wp-content/themes/shriram-college:z" \
	-v "$ROOT:/project:z" \
	--entrypoint sleep docker.io/library/wordpress:cli infinity >/dev/null

echo "Pod $POD created: http://localhost:$PORT"
echo "Next: scripts/setup.sh   (installs WordPress and loads all pages)"
