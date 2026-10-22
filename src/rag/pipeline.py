import uuid
from src.rag.generation import generate_answer
from src.rag.retrieval import retrieve

# Stockage temporaire en mémoire vive (remplacé par Postgres au Jour 3)
EXCHANGES_STORE: dict[str, dict] = {}
FEEDBACKS_STORE: list[dict] = []


def answer_question(question: str) -> dict:
    """Orchestre la recherche, génère la réponse et mémorise l'échange."""
    exchange_id = str(uuid.uuid4())

    chunks = retrieve(question)
    result = generate_answer(question, chunks)

    # Sauvegarde de l'échange en mémoire
    EXCHANGES_STORE[exchange_id] = {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
        "tokens": result["tokens"],
        "latency": result["latency"],
    }

    print(
        f"[LOG INTERNE] ID: {exchange_id} | Tokens: {result['tokens']} | Latence: {result['latency']:.2f}s"
    )

    return {
        "exchange_id": exchange_id,
        "answer": result["answer"],
        "sources": result["sources"],
        "tokens": result["tokens"],
        "latency": result["latency"],
        "chunks": chunks,
    }


def record_feedback(
    exchange_id: str, rating: str, comment: str | None = None
) -> bool:
    """Vérifie l'existence de l'échange et enregistre le feedback.

    Retourne True si l'échange existe, False sinon.
    """
    if exchange_id not in EXCHANGES_STORE:
        return False

    FEEDBACKS_STORE.append(
        {
            "exchange_id": exchange_id,
            "rating": rating,
            "comment": comment,
        }
    )
    print(f"[FEEDBACK REÇU] ID: {exchange_id} | Note: {rating} | Avis: {comment}")
    return True