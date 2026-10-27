"""Cache de réponses : éviter de repayer une génération pour une question déjà posée.

Deux niveaux, du moins cher au plus cher :

1. **Exact** — comparaison sur la question normalisée (minuscules, sans accents ni
   ponctuation). Coût : une requête SQL.
2. **Sémantique** — similarité cosinus entre l'embedding de la question et ceux des
   questions déjà en cache. Coût : un appel d'embedding (négligeable devant une
   génération), et seulement si le niveau 1 a échoué.

Le cache est **versionné** : la version est un condensat du corpus (`knowledge/`), des
modèles et du prompt. Modifier un document ou une consigne invalide donc automatiquement
les anciennes réponses, sans purge manuelle. Les entrées expirent aussi après
`CACHE_TTL_DAYS`.

Une panne du cache ne doit jamais casser le service : toute erreur est journalisée et
se comporte comme un défaut de cache.
"""

import hashlib
import json
import logging
import os
import re
import unicodedata

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from src.rag.config import (
    CACHE_ENABLED,
    CACHE_MAX_ENTRIES,
    CACHE_SEMANTIC,
    CACHE_SIMILARITY_THRESHOLD,
    CACHE_TTL_DAYS,
    DATABASE_URL,
    EMBEDDING_MODEL,
    KNOWLEDGE_DIR,
    LLM_MODEL,
)
from src.rag.prompt import PROMPT_TEMPLATE, SYSTEM_INSTRUCTION

logger = logging.getLogger("api")

_CACHE_SCHEMA = """
CREATE TABLE IF NOT EXISTS answer_cache (
    id BIGSERIAL PRIMARY KEY,
    cache_version VARCHAR(64) NOT NULL,
    question_norm TEXT NOT NULL,
    question_text TEXT NOT NULL,
    embedding JSONB,
    answer TEXT NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]',
    chunks JSONB NOT NULL DEFAULT '[]',
    hits INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_hit_at TIMESTAMPTZ,
    UNIQUE (cache_version, question_norm)
);
CREATE INDEX IF NOT EXISTS idx_answer_cache_created_at ON answer_cache(created_at);
"""

_pool: ConnectionPool | None = None
_version: str | None = None


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=4,
            timeout=5,
            open=True,
            kwargs={"row_factory": dict_row},
        )
    return _pool


def cache_version() -> str:
    """Condensat du corpus + modèles + prompt, mis en cache en mémoire."""
    global _version
    if _version is not None:
        return _version

    digest = hashlib.sha256()
    digest.update(EMBEDDING_MODEL.encode())
    digest.update(LLM_MODEL.encode())
    digest.update(SYSTEM_INSTRUCTION.encode())
    digest.update(PROMPT_TEMPLATE.encode())

    if KNOWLEDGE_DIR.exists():
        for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
            digest.update(path.name.encode())
            digest.update(hashlib.sha256(path.read_bytes()).digest())

    _version = digest.hexdigest()[:32]
    return _version


def normalize(question: str) -> str:
    """Minuscules, sans accents ni ponctuation : deux formulations proches se rejoignent."""
    text = unicodedata.normalize("NFKD", question.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _embed(question: str) -> list[float]:
    # Import local : évite de charger le SDK Gemini quand le cache est désactivé.
    from src.rag.embeddings import embed_query

    return embed_query(question)


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _row_to_entry(row: dict) -> dict:
    return {
        "id": row["id"],
        "answer": row["answer"],
        "sources": row["sources"] or [],
        "chunks": row["chunks"] or [],
    }


def _fetch_exact(conn, question_norm: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, answer, sources, chunks
            FROM answer_cache
            WHERE cache_version = %s
              AND question_norm = %s
              AND created_at > NOW() - make_interval(days => %s);
            """,
            (cache_version(), question_norm, CACHE_TTL_DAYS),
        )
        row = cur.fetchone()
    return _row_to_entry(row) if row else None


def _fetch_semantic(conn, vector: list[float]) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, answer, sources, chunks, embedding
            FROM answer_cache
            WHERE cache_version = %s
              AND embedding IS NOT NULL
              AND created_at > NOW() - make_interval(days => %s)
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (cache_version(), CACHE_TTL_DAYS, CACHE_MAX_ENTRIES),
        )
        rows = cur.fetchall()

    best_row = None
    best_score = 0.0
    for row in rows:
        score = _cosine(vector, row["embedding"] or [])
        if score > best_score:
            best_row, best_score = row, score

    if best_row is None or best_score < CACHE_SIMILARITY_THRESHOLD:
        return None

    logger.info("Cache sémantique : similarité %.3f", best_score)
    return _row_to_entry(best_row)


def _touch(conn, cache_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE answer_cache SET hits = hits + 1, last_hit_at = NOW() WHERE id = %s;",
            (cache_id,),
        )
    conn.commit()


def init_cache() -> None:
    """Crée la table si besoin et journalise l'état du cache."""
    if not CACHE_ENABLED:
        logger.info("Cache de réponses désactivé (CACHE_ENABLED=0).")
        return

    try:
        with _get_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute(_CACHE_SCHEMA)
            conn.commit()
    except Exception as exc:  # pragma: no cover - dépend de l'infra
        logger.warning("Cache indisponible au démarrage : %s", exc)
        return

    logger.info(
        "Cache actif (version %s, sémantique=%s, seuil=%.2f, TTL=%s j).",
        cache_version(),
        CACHE_SEMANTIC,
        CACHE_SIMILARITY_THRESHOLD,
        CACHE_TTL_DAYS,
    )


def lookup(question: str) -> tuple[dict | None, list[float] | None]:
    """Retourne (entrée en cache ou None, embedding de la question si calculé)."""
    if not CACHE_ENABLED:
        return None, None

    question_norm = normalize(question)

    try:
        with _get_pool().connection() as conn:
            exact = _fetch_exact(conn, question_norm)
            if exact:
                _touch(conn, exact["id"])
                logger.info("Cache exact : question déjà répondue.")
                return exact, None
    except Exception as exc:
        logger.warning("Cache ignoré (lecture) : %s", exc)
        return None, None

    vector = None
    if CACHE_SEMANTIC:
        try:
            vector = _embed(question)
            with _get_pool().connection() as conn:
                similar = _fetch_semantic(conn, vector)
                if similar:
                    _touch(conn, similar["id"])
                    return similar, vector
        except Exception as exc:
            logger.warning("Cache ignoré (sémantique) : %s", exc)

    return None, vector


def store(
    question: str,
    answer: str,
    sources: list[str],
    chunks: list[dict],
    question_vector: list[float] | None = None,
) -> None:
    """Enregistre une réponse générée (sans écraser une entrée existante)."""
    if not CACHE_ENABLED or not answer:
        return

    vector = question_vector
    if CACHE_SEMANTIC and vector is None:
        try:
            vector = _embed(question)
        except Exception as exc:
            logger.warning("Cache : embedding indisponible à l'écriture (%s).", exc)

    try:
        with _get_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO answer_cache
                        (cache_version, question_norm, question_text, embedding,
                         answer, sources, chunks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cache_version, question_norm) DO UPDATE
                        SET answer = EXCLUDED.answer,
                            sources = EXCLUDED.sources,
                            chunks = EXCLUDED.chunks,
                            embedding = COALESCE(EXCLUDED.embedding, answer_cache.embedding);
                    """,
                    (
                        cache_version(),
                        normalize(question),
                        question,
                        json.dumps(vector) if vector else None,
                        answer,
                        json.dumps(sources, ensure_ascii=False),
                        json.dumps(chunks, ensure_ascii=False),
                    ),
                )
            conn.commit()
    except Exception as exc:
        logger.warning("Cache ignoré (écriture) : %s", exc)
