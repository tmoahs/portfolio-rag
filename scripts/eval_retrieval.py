from src.rag.retrieval import retrieve
from eval.test_dataset import TEST_CASES

def evaluate_retrieval():
    print(f"{'Question':<55} | {'Source attendue':<35} | {'Trouvé ?':<8} | {'Rang':<5} | {'Dist. min'}")
    print("-" * 120)

    for case in TEST_CASES:
        query = case["question"]
        expected = case.get("expected_source")
        is_trap = case.get("must_refuse", False)

        chunks = retrieve(query)
        min_dist = chunks[0]["distance"] if chunks else 1.0

        if is_trap:
            # Questions Pièges
            print(f"{query[:52] + '...':<55} | {'(Piège - Aucun)':<35} | {'N/A':<8} | {'-':<5} | {min_dist:.4f}")
            continue

        # Vérification de la présence du document attendu
        # (Adapte c["source"] ou c["metadata"]["source"] selon ton implémentation)
        sources_found = [c.get("source") for c in chunks]

        if expected in sources_found:
            rank = sources_found.index(expected) + 1
            found = "OUI"
        else:
            rank = "-"
            found = "NON"

        print(f"{query[:52] + '...':<55} | {str(expected)[:33]:<35} | {found:<8} | {str(rank):<5} | {min_dist:.4f}")

if __name__ == "__main__":
    evaluate_retrieval()