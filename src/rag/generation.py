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

def generate_answer(question: str, chunks: list[dict]) -> dict:
    if chunks and chunks[0]["distance"] > DISTANCE_THRESHOLD:
        return {
            "answer": "Je ne dispose pas de cette information dans le profil de Thomas Patout. N'hésitez pas à le contacter directement pour en savoir plus.",
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
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_OUTPUT_TOKENS,
            },
        )
        answer = response.text
        tokens = response.usage_metadata.total_token_count
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
            raise GeminiQuotaError("Quota API dépassé.")
        raise GeminiServiceError(f"Erreur du service LLM : {e}")

    latency = time.time() - start_time

    sources = list(set(c["source"] for c in chunks))

    refusal_markers = [
        "ne dispose pas",
        "ne peux pas",
        "ne suis pas en mesure",
        "pas d'informations concernant",
        "pas autorisé",
    ]
    if any(marker in answer.lower() for marker in refusal_markers):
        sources = []

    return {
        "answer": answer,
        "sources": sources,
        "latency": latency,
        "chunks": chunks,
        "tokens": tokens
    }