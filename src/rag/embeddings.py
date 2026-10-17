from google import genai
from src.rag.config import EMBEDDING_MODEL
import time
from dotenv import load_dotenv
load_dotenv()

genai_client = genai.Client()

def embed_query(query: str) -> list[float]:
    result = genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config={"task_type": "RETRIEVAL_QUERY"}
    )
    return result.embeddings[0].values


def embed_documents(texts: list[str], batch_size: int = 20, max_retries: int = 3) -> list[list[float]]:
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Gestion des retries pour ce lot
        for attempt in range(max_retries):
            try:
                batch_vectors = []
                for text in batch:
                    result = genai_client.models.embed_content(
                        model=EMBEDDING_MODEL,
                        contents=text,
                        config={"task_type": "RETRIEVAL_DOCUMENT"}
                    )
                    batch_vectors.append(result.embeddings[0].values)

                # Le lot entier a réussi, on valide
                all_embeddings.extend(batch_vectors)
                break
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    sleep_time = 2 ** attempt
                    print(f"Quota atteint (429). Pause de {sleep_time}s avant nouvel essai...")
                    time.sleep(sleep_time)
                else:
                    raise e

    return all_embeddings

if __name__ == "__main__":
    p1 = "Je développe des applications en Python et FastAPI."
    p2 = "J'écris du code backend avec FastAPI et le langage Python."
    p3 = "La recette de la tarte aux pommes demande de la farine et du beurre."

    vectors = embed_documents([p1, p2, p3])

    # 1. Vérification des dimensions
    dims = [len(v) for v in vectors]
    print(f"Dimensions des vecteurs : {dims}")

    # 2. Vérification de la similarité sémantique (produit scalaire)
    sim_1_2 = sum(a * b for a, b in zip(vectors[0], vectors[1]))
    sim_1_3 = sum(a * b for a, b in zip(vectors[0], vectors[2]))

    print(f"Similarité entre phrase 1 et phrase 2 (proches) : {sim_1_2:.4f}")
    print(f"Similarité entre phrase 1 et phrase 3 (éloignées) : {sim_1_3:.4f}")