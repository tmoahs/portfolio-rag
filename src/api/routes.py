import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from psycopg import AsyncConnection
from starlette.background import BackgroundTask

from src.api.db import get_db_connection, save_exchange, save_feedback
from src.api.limiter import limiter
from src.api.security import enforce_daily_quota
from src.api.schemas import (
    AnswerResponse,
    FeedbackRequest,
    FeedbackResponse,
    QuestionRequest,
)
from src.rag.config import RATE_LIMIT_ASK, RATE_LIMIT_FEEDBACK
from src.rag.generation import GeminiQuotaError, GeminiServiceError
from src.rag.pipeline import answer_question, answer_question_stream

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


def _bypass_cache(request: Request) -> bool:
    """En-tête interne pour mesurer le vrai pipeline (évaluations, tests)."""
    return request.headers.get("x-bypass-cache", "").strip().lower() in {"1", "true", "yes"}


@router.post(
    "/ask",
    response_model=AnswerResponse,
    dependencies=[Depends(enforce_daily_quota)],
)
@limiter.limit(RATE_LIMIT_ASK)
def ask(
    request: Request,
    payload: QuestionRequest,
    background_tasks: BackgroundTasks,
):
    try:
        response_data = answer_question(
            payload.question, use_cache=not _bypass_cache(request)
        )

        # Planification de la persistance en tâche de fond (non bloquante)
        background_tasks.add_task(
            save_exchange,
            exchange_data={
                "id": response_data["exchange_id"],
                "user_query": payload.question,
                "response_text": response_data["answer"],
                "latency_seconds": response_data.get("latency"),
                "token_count": response_data.get("tokens"),
                # Une réponse servie par le cache n'a pas appelé le modèle :
                # les statistiques de latence et de coût peuvent l'exclure.
                "model_called": not response_data.get("cached", False),
                "config_version": "cache" if response_data.get("cached") else "v1.0",
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


def _sse(payload: dict) -> str:
    """Formate un événement Server-Sent Events (une ligne `data:` + saut de ligne)."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _persist_stream_exchange(exchange_data: dict, state: dict) -> None:
    """Persiste l'échange une fois le flux terminé (exécuté en tâche de fond)."""
    if not exchange_data.get("id"):
        return
    await save_exchange(exchange_data=exchange_data, chunks=state["chunks"])


@router.post("/ask/stream", dependencies=[Depends(enforce_daily_quota)])
@limiter.limit(RATE_LIMIT_ASK)
def ask_stream(request: Request, payload: QuestionRequest):
    """Variante en flux de /ask : la réponse est poussée au fil de l'eau (SSE).

    Événements émis :
      {"type": "meta",    "exchange_id": ...}
      {"type": "sources", "chunks": [...]}
      {"type": "delta",   "text": "..."}
      {"type": "done",    "exchange_id", "answer", "sources", "latency", "tokens"}
      {"type": "error",   "status", "message"}
    """
    exchange_data = {
        "id": None,
        "user_query": payload.question,
        "response_text": None,
        "latency_seconds": None,
        "token_count": None,
    }
    state: dict = {"chunks": []}
    use_cache = not _bypass_cache(request)

    def event_stream():
        # Commentaire SSE : ouvre le flux immédiatement, avant l'appel au modèle.
        yield ": stream-start\n\n"

        try:
            for kind, data in answer_question_stream(
                payload.question, use_cache=use_cache
            ):
                if kind == "meta":
                    exchange_data["id"] = data["exchange_id"]
                    yield _sse({"type": "meta", "exchange_id": data["exchange_id"]})
                elif kind == "sources":
                    state["chunks"] = data["chunks"]
                    yield _sse({"type": "sources", "chunks": data["chunks"]})
                elif kind == "delta":
                    yield _sse({"type": "delta", "text": data})
                elif kind == "done":
                    exchange_data["response_text"] = data["answer"]
                    exchange_data["latency_seconds"] = data["latency"]
                    exchange_data["token_count"] = data["tokens"]
                    if data.get("cached"):
                        exchange_data["model_called"] = False
                        exchange_data["config_version"] = "cache"
                    yield _sse({"type": "done", **data})

        except GeminiQuotaError:
            logger.warning("Quota Gemini atteint (flux).")
            yield _sse({
                "type": "error",
                "status": 429,
                "message": "Le service est temporairement saturé. Merci de réessayer dans un instant.",
            })
        except GeminiServiceError as e:
            logger.error(f"Erreur interne LLM (flux) : {e}")
            yield _sse({
                "type": "error",
                "status": 503,
                "message": "Le service de réponse est momentanément indisponible.",
            })
        except Exception as e:
            logger.error(f"Erreur inattendue (flux) : {e}")
            yield _sse({
                "type": "error",
                "status": 500,
                "message": "Une erreur interne s'est produite lors du traitement.",
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
        background=BackgroundTask(_persist_stream_exchange, exchange_data, state),
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