#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p backups
STAMP="$(date +%Y%m%d-%H%M%S)"
DB_CONTAINER="contractor-erp-db"
ODOO_CONTAINER="contractor-erp-odoo"
DB_USER="${POSTGRES_USER:-odoo}"
DB_NAME="${ODOO_DB_NAME:-contractor_erp}"

docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "backups/${DB_NAME}-${STAMP}.sql.gz"
docker run --rm --volumes-from "$ODOO_CONTAINER" -v "$ROOT_DIR/backups:/backup" busybox sh -c "tar czf /backup/odoo-filestore-${STAMP}.tar.gz /var/lib/odoo/filestore || true"
find backups -type f -mtime +14 -delete
printf 'Backup completed: %s\n' "$STAMP"
