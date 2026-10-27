#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Sauvegarde quotidienne de Postgres (à lancer par cron sur le serveur).
#
#   crontab -e
#   15 3 * * * cd /srv/portfolio-rag && ./deploy/backup_postgres.sh >> /var/log/portfolio-backup.log 2>&1
#
# Variables optionnelles :
#   BACKUP_DIR              (défaut : ./backups)
#   BACKUP_RETENTION_DAYS   (défaut : 14)
#   RCLONE_REMOTE           ex. "b2:mon-bucket/portfolio" pour copier hors serveur
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")/.."

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION="${BACKUP_RETENTION_DAYS:-14}"
ENV_FILE="${ENV_FILE:-.env.prod}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Fichier $ENV_FILE introuvable." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "./$ENV_FILE"
set +a

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y-%m-%d_%H%M)"
OUT="$BACKUP_DIR/portfolio_${STAMP}.sql.gz"

echo "[$(date -Is)] Sauvegarde Postgres -> $OUT"
docker compose --env-file "$ENV_FILE" \
  -f docker-compose.yml -f docker-compose.prod.yml \
  exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  | gzip -9 > "$OUT"

# Vérifie que le fichier n'est pas vide avant de faire du ménage.
if [[ ! -s "$OUT" ]]; then
  echo "Sauvegarde vide : échec." >&2
  rm -f "$OUT"
  exit 1
fi

find "$BACKUP_DIR" -name 'portfolio_*.sql.gz' -mtime "+$RETENTION" -delete

if [[ -n "${RCLONE_REMOTE:-}" ]] && command -v rclone >/dev/null 2>&1; then
  echo "[$(date -Is)] Copie hors serveur -> $RCLONE_REMOTE"
  rclone copy "$OUT" "$RCLONE_REMOTE"
fi

echo "[$(date -Is)] OK ($(du -h "$OUT" | cut -f1))"
