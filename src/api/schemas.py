from typing import Literal, Optional
from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="La question posée par l'utilisateur",
        example="Quels sont les projets en machine learning de Thomas ?",
    )


class AnswerResponse(BaseModel):
    exchange_id: str = Field(
        ...,
        description="Identifiant unique de l'échange pour le feedback",
    )
    answer: str = Field(
        ...,
        description="Réponse synthétisée par l'assistant",
    )
    sources: list[str] = Field(
        ...,
        description="Liste des documents sources utilisés",
    )


class FeedbackRequest(BaseModel):
    exchange_id: str = Field(
        ...,
        description="UUID de l'échange concerné",
    )
    rating: Literal["positive", "negative"] = Field(
        ...,
        description="Note de l'échange : 'positive' ou 'negative'",
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=280,
        description="Commentaire court facultatif",
    )


class FeedbackResponse(BaseModel):
    status: str
    message: str