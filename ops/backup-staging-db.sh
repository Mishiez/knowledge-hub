#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-$HOME/knowledge-hub-staging/docker-compose.staging.yml}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/knowledge-hub-staging/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

timestamp=$(date -u '+%Y%m%dT%H%M%SZ')
backup_file="$BACKUP_DIR/knowledgehub-$timestamp.dump"

docker compose -f "$COMPOSE_FILE" exec -T staging-db \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > "$backup_file"

if [[ ! -s "$backup_file" ]]; then
  rm -f "$backup_file"
  echo "Backup was empty: $backup_file" >&2
  exit 1
fi

sha256sum "$backup_file" > "$backup_file.sha256"

find "$BACKUP_DIR" -type f -name 'knowledgehub-*.dump' \
  -mtime "+$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -type f -name 'knowledgehub-*.dump.sha256' \
  -mtime "+$RETENTION_DAYS" -delete

echo "Created backup: $backup_file"
echo "Removed dump files older than $RETENTION_DAYS days"