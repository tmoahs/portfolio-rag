import chromadb

from src.rag.config import DATA_DIR

def get_collection():
    chroma_client = chromadb.PersistentClient(path=str(DATA_DIR))
    collection = chroma_client.get_or_create_collection(
        name="rag_collection",
        configuration={"hnsw": {"space": "cosine"}}
    )

    return collection

def upsert_chunks(collection, chunks, embeddings):
    collection.upsert(
        ids = [c["id"] for c in chunks],
        embeddings=embeddings,
        documents = [c["text"] for c in chunks],
        metadatas = [{"source": c["source"], "title": c["title"]} for c in chunks]
    )

def query_collection(collection, query_vector, n_results: int = 5):
    results = collection.query(query_embeddings=[query_vector], n_results=n_results)
    return results