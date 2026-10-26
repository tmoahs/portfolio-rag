import json
import time
from datetime import datetime
import requests
from pathlib import Path

from src.rag.config import LLM_MODEL, TOP_K
from src.rag.retrieval import retrieve
from eval.test_dataset import TEST_CASES

# Configuration
EVAL_CONFIG = {
    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "top_k": TOP_K,
    "model": LLM_MODEL,
    "temperature": 0.0,
    "api_url": "http://127.0.0.1:8000/ask"
}

CACHE_FILE = Path("eval/eval_cache.json")


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)


def evaluate_retrieval(cases):
    """Évalue uniquement la base vectorielle (Hit@k, MRR)"""
    results = []
    hits = 0
    mrr_sum = 0.0

    for case in cases:
        if case.get("must_refuse"):
            continue

        query = case["question"]
        expected = case["expected_source"]

        chunks = retrieve(query)
        sources_found = [c.get("source") for c in chunks]

        hit = expected in sources_found
        rank = sources_found.index(expected) + 1 if hit else 0
        mrr = 1.0 / rank if rank > 0 else 0.0

        if hit: hits += 1
        mrr_sum += mrr

        results.append({"query": query, "hit": hit, "rank": rank, "mrr": mrr})

    total = len(results)
    print(f"--- RÉSULTATS RECHERCHE ---")
    print(f"Hit@{EVAL_CONFIG['top_k']} : {hits / total:.2%} ({hits}/{total})")
    print(f"MRR   : {mrr_sum / total:.3f}\n")
    return results


def evaluate_generation(cases):
    """Évalue la chaîne complète avec mise en cache"""
    results = []
    cache = load_cache()

    print(f"{'Question':<45} | {'Exactitude':<12} | {'Latence (s)'}")
    print("-" * 75)

    for case in cases:
        query = case["question"]
        expected_facts = case.get("expected_facts", [])
        must_refuse = case.get("must_refuse", False)

        # Vérification du cache
        if query in cache:
            answer = cache[query]
            latency = 0.0
        else:
            start_time = time.time()
            try:
                response = requests.post(EVAL_CONFIG["api_url"], json={"question": query})
                answer = response.json().get("answer", "")
                latency = time.time() - start_time

                # Sauvegarde immédiate dans le cache
                cache[query] = answer
                save_cache(cache)
            except Exception as e:
                print(f"Erreur API pour: {query[:30]}... ({e})")
                continue

        # Calcul de l'exactitude
        facts_found = sum(1 for fact in expected_facts if fact.lower() in answer.lower())
        accuracy = (facts_found / len(expected_facts)) if expected_facts else 1.0

        if must_refuse:
            refused = any(word in answer.lower() for word in [
                "ne sais pas", "désolé", "pas mentionné", "aucune information",
                "ne précisent pas", "ne peux pas répondre", "ne dispose pas de cet élément"
            ])
            accuracy = 1.0 if refused else 0.0

        results.append({
            "query": query,
            "answer": answer,
            "accuracy": accuracy,
            "latency": latency,
            "must_refuse": must_refuse
        })

        lat_str = f"{latency:.2f}s" if latency > 0 else "(cache)"
        print(f"{query[:42] + '...':<45} | {accuracy:>10.0%} | {lat_str}")

    avg_acc = sum(r["accuracy"] for r in results) / len(results)
    print(f"\n--- RÉSULTATS GÉNÉRATION ---")
    print(f"Exactitude moyenne : {avg_acc:.2%}\n")

    return results


def save_results(retrieval_res, generation_res):
    """Sauvegarde le rapport final"""
    Path("eval/results").mkdir(parents=True, exist_ok=True)
    filename = f"eval/results/eval_{EVAL_CONFIG['timestamp']}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"config": EVAL_CONFIG, "retrieval": retrieval_res, "generation": generation_res}, f,
                  ensure_ascii=False, indent=2)
    print(f"Rapport sauvegardé dans : {filename}")


if __name__ == "__main__":
    print(f"Démarrage de l'évaluation ({EVAL_CONFIG['timestamp']})\n")
    retrieval_data = evaluate_retrieval(TEST_CASES)
    generation_data = evaluate_generation(TEST_CASES)
    save_results(retrieval_data, generation_data)