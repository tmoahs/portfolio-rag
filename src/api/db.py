from collections.abc import AsyncGenerator
from psycopg import AsyncConnection
import logging
from psycopg_pool import AsyncConnectionPool
from src.rag.config import DATABASE_URL
from src.rag.config import LLM_MODEL

db_pool: AsyncConnectionPool | None = None

# ---------------------------------------------------------------------------
async def init_db_pool() -> None:
    global db_pool
    db_pool = AsyncConnectionPool(
        conninfo=DATABASE_URL,
        min_size=1,
        max_size=10,
        open=False,
    )
    await db_pool.open()

# ---------------------------------------------------------------------------
async def close_db_pool() -> None:
    global db_pool
    if db_pool is not None:
        await db_pool.close()

# ---------------------------------------------------------------------------
async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    if db_pool is None:
        raise RuntimeError("Le pool de base de données n'est pas initialisé.")
    async with db_pool.connection() as conn:
        yield conn

# ---------------------------------------------------------------------------
logger = logging.getLogger("api")

async def save_exchange(exchange_data: dict, chunks: list[dict]) -> None:
    if db_pool is None:
        logger.error(
            "Impossible d'enregistrer l'échange : pool de base de données non initialisé."
        )
        return

    try:
        async with db_pool.connection() as conn:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    # 1. Insertion de l'échange principal
                    insert_exchange_query = """
                        INSERT INTO exchanges (
                            id, user_query, rewritten_query, response_text,
                            latency_seconds, token_count, model_name,
                            top_distance, model_called, config_version
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    top_distance = chunks[0]["distance"] if chunks else None

                    await cur.execute(
                        insert_exchange_query,
                        (
                            exchange_data["id"],
                            exchange_data["user_query"],
                            exchange_data.get("rewritten_query"),
                            exchange_data.get("response_text"),
                            exchange_data.get("latency_seconds"),
                            exchange_data.get("token_count"),
                            exchange_data.get("model_name", LLM_MODEL),
                            top_distance,
                            exchange_data.get("model_called", True),
                            exchange_data.get("config_version", "v1.0"),
                        ),
                    )

                    # 2. Insertion des chunks associés
                    if chunks:
                        insert_chunks_query = """
                            INSERT INTO retrieved_chunks (
                                exchange_id, chunk_id, rank, distance, used_in_response
                            )
                            VALUES (%s, %s, %s, %s, %s);
                        """
                        chunks_tuples = [
                            (
                                exchange_data["id"],
                                chunk.get(
                                    "id", f"{chunk.get('source', 'chunk')}_{rank}"
                                ),
                                rank,
                                chunk["distance"],
                                chunk.get("used_in_response", True),
                            )
                            for rank, chunk in enumerate(chunks, start=1)
                        ]

                        await cur.executemany(insert_chunks_query, chunks_tuples)

    except Exception as e:
        # Règle d'or : une erreur de log ne doit jamais bloquer le reste
        logger.error(
            f"Erreur lors de la persistance de l'échange {exchange_data.get('id')}: {e}"
        )

# ---------------------------------------------------------------------------
async def save_feedback(
        exchange_id: str, rating: str | int, comment: str | None
) -> bool:
    rating_value = 1 if rating == "positive" else -1 if rating == "negative" else int(rating)

    if db_pool is None:
        logger.error(
            "Impossible d'enregistrer le feedback : pool de base de données non initialisé."
        )
        return False

    try:
        async with db_pool.connection() as conn:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    # 1. Vérification que l'échange existe bien
                    await cur.execute(
                        "SELECT 1 FROM exchanges WHERE id = %s;", (exchange_id,)
                    )
                    if await cur.fetchone() is None:
                        return False

                    # 2. Insertion ou mise à jour (UPSERT)
                    upsert_query = """
                                   INSERT INTO feedbacks (exchange_id, rating, comment)
                                   VALUES (%s, %s, %s)
                                   ON CONFLICT (exchange_id)
                                       DO UPDATE SET rating     = EXCLUDED.rating,
                                                     comment    = EXCLUDED.comment,
                                                     created_at = NOW(); \
                                   """
                    await cur.execute(
                        upsert_query, (exchange_id, rating_value, comment)
                    )
                    return True
    except Exception as e:
        logger.error(
            f"Erreur lors de l'enregistrement du feedback pour {exchange_id}: {e}"
        )
        return False