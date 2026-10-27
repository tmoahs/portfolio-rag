import re
import time
from src.rag.prompt import SYSTEM_INSTRUCTION
from src.rag.prompt import PROMPT_TEMPLATE
from src.rag.config import TEMPERATURE
from src.rag.config import DISTANCE_THRESHOLD
from src.rag.config import MAX_OUTPUT_TOKENS
from src.rag.config import LLM_MODEL
from google import genai
from google.genai.errors import APIError

class GeminiQuotaError(Exception):
    pass


class GeminiServiceError(Exception):
    pass

def format_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(f"[Extrait {i} - Source : {c['source']}]\n{c['text']}")
    return "\n\n".join(parts)

genai_client = genai.Client()

# Réponse de repli quand aucun document n'est assez proche de la question.
REFUSAL_ANSWER = (
    "Je ne dispose pas de cette information dans le profil de Thomas Patout. "
    "N'hésitez pas à le contacter directement pour en savoir plus."
)

# Formules qui signalent un refus du modèle : dans ce cas on masque les sources.
# Expressions régulières : les formulations varient d'une génération à l'autre.
REFUSAL_PATTERNS = [
    r"ne dispose pas",
    r"ne peux (?:donc )?(?:pas )?(?:te |vous )?répondre",
    r"ne suis pas en mesure",
    r"pas en mesure de (?:te |vous )?répondre",
    r"pas d'informations? (?:concernant|sur)",
    r"pas autorisé",
    r"assistant (?:uniquement |exclusivement )?dédié",
    r"dédié (?:uniquement |exclusivement )?au (?:profil|parcours)",
    r"hors (?:de mon|du) (?:périmètre|cadre|champ)",
    r"culture générale",
]

GENERATION_CONFIG = {
    "system_instruction": SYSTEM_INSTRUCTION,
    "temperature": TEMPERATURE,
    "max_output_tokens": MAX_OUTPUT_TOKENS,
}


def _raise_llm_error(error: Exception) -> None:
    """Traduit une erreur du SDK Google en erreur métier explicite."""
    err_msg = str(error).lower()
    if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
        raise GeminiQuotaError("Quota API dépassé.") from error
    raise GeminiServiceError(f"Erreur du service LLM : {error}") from error


def _is_refusal(answer: str) -> bool:
    return any(
        re.search(pattern, answer, flags=re.IGNORECASE)
        for pattern in REFUSAL_PATTERNS
    )


def _sources_for(answer: str, chunks: list[dict]) -> list[str]:
    """Liste les documents cités, vidée si le modèle refuse de répondre."""
    if _is_refusal(answer):
        return []
    return list(dict.fromkeys(c["source"] for c in chunks))


def generate_answer(question: str, chunks: list[dict]) -> dict:
    if chunks and chunks[0]["distance"] > DISTANCE_THRESHOLD:
        return {
            "answer": REFUSAL_ANSWER,
            "sources": [],
            "latency": 0.0,
            "tokens": 0
        }

    context_str = format_context(chunks)
    user_prompt = PROMPT_TEMPLATE.format(context=context_str, question=question)

    start_time = time.time()

    try:
        response = genai_client.models.generate_content(
            model=LLM_MODEL,
            contents=user_prompt,
            config=GENERATION_CONFIG,
        )
        answer = response.text
        tokens = response.usage_metadata.total_token_count
    except Exception as e:
        _raise_llm_error(e)

    latency = time.time() - start_time

    return {
        "answer": answer,
        "sources": _sources_for(answer, chunks),
        "latency": latency,
        "chunks": chunks,
        "tokens": tokens
    }


def generate_answer_stream(question: str, chunks: list[dict]):
    """Variante en flux de generate_answer.

    Générateur qui produit des tuples (type, payload) :
      - ("delta", str)  : un morceau de texte à ajouter à la réponse ;
      - ("done", dict)  : la réponse complète et ses métadonnées.
    """
    if chunks and chunks[0]["distance"] > DISTANCE_THRESHOLD:
        yield "delta", REFUSAL_ANSWER
        yield "done", {
            "answer": REFUSAL_ANSWER,
            "sources": [],
            "latency": 0.0,
            "tokens": 0,
        }
        return

    context_str = format_context(chunks)
    user_prompt = PROMPT_TEMPLATE.format(context=context_str, question=question)

    start_time = time.time()
    parts: list[str] = []
    tokens = 0

    try:
        stream = genai_client.models.generate_content_stream(
            model=LLM_MODEL,
            contents=user_prompt,
            config=GENERATION_CONFIG,
        )

        for item in stream:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
                yield "delta", text

            usage = getattr(item, "usage_metadata", None)
            total = getattr(usage, "total_token_count", None) if usage else None
            if total:
                tokens = total
    except Exception as e:
        _raise_llm_error(e)

    answer = "".join(parts)

    yield "done", {
        "answer": answer,
        "sources": _sources_for(answer, chunks),
        "latency": time.time() - start_time,
        "tokens": tokens,
    }