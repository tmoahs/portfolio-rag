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


class SourceChunk(BaseModel):
    """Extrait de document réellement envoyé au modèle (affiché en accordéon)."""

    text: str = Field(..., description="Texte du chunk utilisé pour répondre")
    source: str = Field(..., description="Fichier d'origine du chunk")
    title: Optional[str] = Field(
        default=None, description="Titre lisible du document source"
    )
    distance: Optional[float] = Field(
        default=None, description="Distance cosinus avec la question (plus bas = plus proche)"
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
    chunks: list[SourceChunk] = Field(
        default_factory=list,
        description="Extraits de documents utilisés, affichés en détail dans l'interface",
    )
    cached: bool = Field(
        default=False,
        description="Vrai si la réponse provient du cache (aucun appel au modèle)",
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