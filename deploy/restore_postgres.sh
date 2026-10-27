#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Restauration d'une sauvegarde Postgres.
# À tester au moins une fois : une sauvegarde jamais restaurée n'est qu'une
# hypothèse.
#
#   ./deploy/restore_postgres.sh backups/portfolio_2026-10-27_0315.sql.gz
#
# ATTENTION : écrase le contenu actuel de la base applicative.
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")/.."

ARCHIVE="${1:-}"
ENV_FILE="${ENV_FILE:-.env.prod}"

if [[ -z "$ARCHIVE" || ! -f "$ARCHIVE" ]]; then
  echo "Usage : $0 <sauvegarde.sql.gz>" >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Fichier $ENV_FILE introuvable." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "./$ENV_FILE"
set +a

read -r -p "Remplacer le contenu de '$POSTGRES_DB' par $ARCHIVE ? [oui/non] " CONFIRM
if [[ "$CONFIRM" != "oui" ]]; then
  echo "Annulé."
  exit 0
fi

echo "[$(date -Is)] Restauration en cours..."
gunzip -c "$ARCHIVE" | docker compose --env-file "$ENV_FILE" \
  -f docker-compose.yml -f docker-compose.prod.yml \
  exec -T postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "[$(date -Is)] Restauration terminée. Vérifie /api/health puis une question de test."
