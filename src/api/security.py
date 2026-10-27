"""Garde-fous de production : plafond quotidien et politique de conservation.

Aucune adresse IP n'est journalisée ni stockée : la limitation par IP est
purement en mémoire (slowapi) et le quota quotidien se base sur le nombre
d'échanges enregistrés dans Postgres.
"""

import logging
import os

from fastapi import HTTPException, status

from src.api import db

logger = logging.getLogger("api")

# 0 (ou négatif) désactive le plafond : pratique en développement.
DAILY_QUESTION_LIMIT = int(os.getenv("DAILY_QUESTION_LIMIT", "0"))

RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "365"))


async def enforce_daily_quota() -> None:
    """Refuse la question si le plafond global du jour est atteint.

    En cas d'erreur base (indisponible), on laisse passer : le service reste
    utilisable et l'échec est journalisé. Le plafond protège la facture, pas
    la confidentialité.
    """
    if DAILY_QUESTION_LIMIT <= 0:
        return

    pool = getattr(db, "db_pool", None)
    if pool is None:
        return

    try:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT count(*) FROM exchanges "
                    "WHERE created_at >= date_trunc('day', NOW());"
                )
                row = await cur.fetchone()
    except Exception as exc:  # pragma: no cover - dépend de l'infra
        logger.warning("Quota quotidien non vérifiable : %s", exc)
        return

    used = int(row[0]) if row else 0
    if used >= DAILY_QUESTION_LIMIT:
        logger.warning(
            "Quota quotidien atteint (%s/%s), question refusée.",
            used,
            DAILY_QUESTION_LIMIT,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Le quota quotidien de questions est atteint. "
                "Merci de réessayer demain."
            ),
        )
