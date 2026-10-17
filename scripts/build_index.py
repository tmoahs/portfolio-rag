import time
import chromadb

# Emplacements
from src.rag.config import KNOWLEDGE_DIR
from src.rag.config import CHUNK_SIZE

# Fonctions
from src.rag.loader import load_documents
from src.rag.chunker import chunk_all_documents
from src.rag.embeddings import embed_documents
from src.rag.vectorstore import get_collection
from src.rag.vectorstore import upsert_chunks

start_time = time.time()

# 1. Chargement
documents = load_documents(KNOWLEDGE_DIR)

# 2. Découpage
chunks = chunk_all_documents(documents, max_chunk_size=CHUNK_SIZE)

# 3. Embeddings
texts = [c["text"] for c in chunks]
embeddings = embed_documents(texts)

# 4. Base vectorielle
collection = get_collection()

# Vider la collection avant réinsertion
existing_ids = collection.get()["ids"]
if existing_ids:
    collection.delete(ids=existing_ids)

# Insertion
upsert_chunks(collection, chunks, embeddings)

duration = time.time() - start_time

print("Nombre de documents : ", len(documents))
print("Nombre de chunks : ", len(chunks))
print("Nombre d'éléments dans la collection ': ", collection.count())
print("Durée d'execution : ", duration)