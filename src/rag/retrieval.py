from src.rag.config import TOP_K
from src.rag.embeddings import embed_query
from src.rag.vectorstore import get_collection
from src.rag.vectorstore import query_collection

def retrieve(query: str, top_k: int = TOP_K):
    search_query = query
    if "thomas" not in query.lower() and "patout" not in query.lower():
        search_query = f"{query} (Thomas Patout)"
    query_vector = embed_query(search_query)
    collection = get_collection()
    results = query_collection(collection, query_vector, n_results=top_k)

    retrieved = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        retrieved.append({
            "text": doc,
            "source": meta["source"],
            "title": meta["title"],
            "distance": dist
        })
    return retrieved

if __name__ == "__main__":
    question = "Quelles sont tes compétences avec Python ?"
    chunks = retrieve(question, top_k=3)

    print(f"Question : {question}\n")
    for i, c in enumerate(chunks, start=1):
        print(f"Rang {i} | Source : {c['source']} | Titre : {c['title']} | Distance : {c['distance']:.4f}")
        print(f"Texte : {c['text'][:150]}...")
        print("-" * 40)