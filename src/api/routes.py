import logging
from fastapi import APIRouter, HTTPException, Request, status
from src.api.limiter import limiter
from src.api.schemas import (
    AnswerResponse,
    FeedbackRequest,
    FeedbackResponse,
    QuestionRequest,
)
from src.rag.config import RATE_LIMIT_ASK, RATE_LIMIT_FEEDBACK
from src.rag.generation import GeminiQuotaError, GeminiServiceError
from src.rag.pipeline import answer_question, record_feedback

logger = logging.getLogger("api")
router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/ask", response_model=AnswerResponse)
@limiter.limit(RATE_LIMIT_ASK)
def ask(request: Request, payload: QuestionRequest):
    try:
        return answer_question(payload.question)
    except GeminiQuotaError:
        logger.warning("Quota Gemini atteint.")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Le service est temporairement saturé en raison d'une forte demande. Merci de réessayer dans un instant.",
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
def submit_feedback(request: Request, payload: FeedbackRequest):
    success = record_feedback(
        exchange_id=payload.exchange_id,
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