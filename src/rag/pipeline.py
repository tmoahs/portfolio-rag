import uuid
from src.rag.cache import lookup as cache_lookup
from src.rag.cache import store as cache_store
from src.rag.generation import generate_answer, generate_answer_stream
from src.rag.retrieval import retrieve

# Stockage temporaire en mémoire vive (remplacé par Postgres au Jour 3)
EXCHANGES_STORE: dict[str, dict] = {}
FEEDBACKS_STORE: list[dict] = []


def answer_question(question: str, use_cache: bool = True) -> dict:
    """Orchestre la recherche, génère la réponse et mémorise l'échange.

    `use_cache=False` court-circuite lecture et écriture : indispensable pour les
    évaluations, qui doivent mesurer le vrai pipeline et ne pas polluer le cache.
    """
    exchange_id = str(uuid.uuid4())

    cached, question_vector = (cache_lookup(question) if use_cache else (None, None))
    if cached:
        chunks = cached["chunks"]
        result = {
            "answer": cached["answer"],
            "sources": cached["sources"],
            "latency": 0.0,
            "tokens": 0,
        }
        print(f"[CACHE] Réponse servie depuis le cache : {question[:60]}")
    else:
        chunks = retrieve(question)
        result = generate_answer(question, chunks)
        if use_cache:
            cache_store(
                question,
                result["answer"],
                result["sources"],
                chunks,
                question_vector=question_vector,
            )

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
        "cached": bool(cached),
    }


def answer_question_stream(question: str, use_cache: bool = True):
    """Variante en flux de answer_question (SSE).

    Générateur d'événements (type, payload) :
      - ("meta", dict)    : identifiant de l'échange, envoyé en premier ;
      - ("sources", dict) : les extraits retrouvés, avant la génération ;
      - ("delta", str)    : un morceau de la réponse ;
      - ("done", dict)    : réponse finale, sources retenues, latence, tokens.
    """
    exchange_id = str(uuid.uuid4())
    cached, question_vector = (cache_lookup(question) if use_cache else (None, None))

    yield "meta", {"exchange_id": exchange_id}

    if cached:
        chunks = cached["chunks"]
        yield "sources", {
            "chunks": chunks,
            "sources": cached["sources"],
        }
        yield "delta", cached["answer"]

        EXCHANGES_STORE[exchange_id] = {
            "question": question,
            "answer": cached["answer"],
            "sources": cached["sources"],
            "tokens": 0,
            "latency": 0.0,
        }
        print(f"[CACHE] Réponse en flux servie depuis le cache : {question[:60]}")

        yield "done", {
            "exchange_id": exchange_id,
            "answer": cached["answer"],
            "sources": cached["sources"],
            "latency": 0.0,
            "tokens": 0,
            "cached": True,
        }
        return

    chunks = retrieve(question)
    yield "sources", {
        "chunks": chunks,
        "sources": list(dict.fromkeys(c["source"] for c in chunks)),
    }

    answer = ""
    meta = {"answer": "", "sources": [], "latency": 0.0, "tokens": 0}

    for kind, payload in generate_answer_stream(question, chunks):
        if kind == "delta":
            answer += payload
            yield "delta", payload
        elif kind == "done":
            meta = payload

    if use_cache:
        cache_store(
            question,
            answer,
            meta["sources"],
            chunks,
            question_vector=question_vector,
        )

    EXCHANGES_STORE[exchange_id] = {
        "question": question,
        "answer": answer,
        "sources": meta["sources"],
        "tokens": meta["tokens"],
        "latency": meta["latency"],
    }

    print(
        f"[LOG INTERNE] ID: {exchange_id} | Tokens: {meta['tokens']} | Latence: {meta['latency']:.2f}s"
    )

    yield "done", {
        "exchange_id": exchange_id,
        "answer": answer,
        "sources": meta["sources"],
        "latency": meta["latency"],
        "tokens": meta["tokens"],
        "cached": False,
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