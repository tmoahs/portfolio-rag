from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from psycopg import AsyncConnection

from src.api.db import get_db_connection, save_exchange, save_feedback
from src.api.limiter import limiter
from src.api.schemas import (
    AnswerResponse,
    FeedbackRequest,
    FeedbackResponse,
    QuestionRequest,
)
from src.rag.config import RATE_LIMIT_ASK, RATE_LIMIT_FEEDBACK
from src.rag.generation import GeminiQuotaError, GeminiServiceError
from src.rag.pipeline import answer_question
import logging
from fastapi import Depends
from psycopg import AsyncConnection
from src.api.db import get_db_connection

logger = logging.getLogger("api")
router = APIRouter()



@router.get("/health")
async def health_check(conn: AsyncConnection = Depends(get_db_connection)):
    try:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1;")
        return {
            "status": "ok",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Échec de la vérification de santé base de données : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de données indisponible.",
        )


@router.post("/ask", response_model=AnswerResponse)
@limiter.limit(RATE_LIMIT_ASK)
def ask(
    request: Request,
    payload: QuestionRequest,
    background_tasks: BackgroundTasks,
):
    try:
        response_data = answer_question(payload.question)

        # Planification de la persistance en tâche de fond (non bloquante)
        background_tasks.add_task(
            save_exchange,
            exchange_data={
                "id": response_data["exchange_id"],
                "user_query": payload.question,
                "response_text": response_data["answer"],
                "latency_seconds": response_data.get("latency"),
                "token_count": response_data.get("tokens"),
            },
            chunks=response_data.get("chunks", []),
        )

        return response_data

    except GeminiQuotaError:
        logger.warning("Quota Gemini atteint.")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Le service est temporairement saturé. Merci de réessayer dans un instant.",
        )
    except GeminiServiceError as e:
        logger.error(f"Erreur interne LLM : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service de réponse est momentanément indisponible.",
        )
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite lors du traitement.",
        )


@router.post("/feedback", response_model=FeedbackResponse)
@limiter.limit(RATE_LIMIT_FEEDBACK)
async def submit_feedback(request: Request, payload: FeedbackRequest):
    success = await save_feedback(
        exchange_id=str(payload.exchange_id),
        rating=payload.rating,
        comment=payload.comment,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identifiant d'échange introuvable ou expiré.",
        )

    return {
        "status": "ok",
        "message": "Feedback enregistré avec succès.",
    }