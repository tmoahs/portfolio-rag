from src.rag.config import TOP_K
from src.rag.retrieval import retrieve
from eval.test_dataset import TEST_CASES

from eval.test_dataset import TEST_CASES
from src.rag.retrieval import retrieve


def evaluate():
    print(f"{'Question':<55} | {'Source attendue':<25} | {'Trouvé ?':<8} | {'Rang':<5} | {'Dist. min'}")
    print("-" * 110)

    for case in TEST_CASES:
        query = case["question"]
        expected = case["expected_source"]

        chunks = retrieve(query)
        min_dist = chunks[0]["distance"] if chunks else 1.0

        if expected is None:
            # Questions Pièges
            print(f"{query[:52] + '...':<55} | {'(Piège - Aucun)':<25} | {'N/A':<8} | {'-':<5} | {min_dist:.4f}")
            continue

        # Vérification de la présence du document attendu
        sources_found = [c["source"] for c in chunks]

        if expected in sources_found:
            rank = sources_found.index(expected) + 1
            found = "OUI"
        else:
            rank = "-"
            found = "NON"

        print(f"{query[:52] + '...':<55} | {expected:<25} | {found:<8} | {str(rank):<5} | {min_dist:.4f}")


if __name__ == "__main__":
    evaluate()