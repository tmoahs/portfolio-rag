import os
import sys
from dotenv import load_dotenv

# Test Clé API

# 1. Charge le fichier .env dans les variables d'environnement
if not load_dotenv():
    print("Attention : Aucun fichier .env n'a été détecté ou chargé.", file=sys.stderr)

# 2. Lit la variable d'environnement
KEY_NAME = "GEMINI_API_KEY"
api_key = os.getenv(KEY_NAME)

# 3. Arrêt propre si la clé est absente ou vide
if not api_key:
    print(f"Erreur critique : La variable '{KEY_NAME}' est absente du fichier .env ou vide.", file=sys.stderr)
    sys.exit(1)

# 4. Affiche une confirmation sécurisée
print(f"Clé '{KEY_NAME}' trouvée avec succès ! (Début de la clé : {api_key[:4]}...)")

# Test Gemini
from google import genai

genai_client = genai.Client()

# 1. Génération de texte
interaction = genai_client.interactions.create(
    model="gemini-3.8-flash",
    input="How does AI work? very small text"
)
print("--- Texte généré ---")
print(interaction.output_text)

# 2. Embedding direct du texte généré plus haut
result = genai_client.models.embed_content(
    model="gemini-embedding-2",
    contents=interaction.output_text,
    config={"task_type": "RETRIEVAL_DOCUMENT"} # On réutilise la sortie ici
)

# Accès au vecteur de nombres
vector = result.embeddings[0].values

print("\n--- Embeddings de la réponse ---")
print(f"Dimension du vecteur : {len(vector)}")
print(f"3 premières valeurs : {vector[:3]}")

# Test ChromaDB
from pathlib import Path
from src.rag.config import DATA_DIR
import chromadb

# 1. Remonter d'un cran au-dessus de scripts/ pour atteindre la racine du projet
ROOT_DIR = Path(__file__).resolve().parent.parent

# 3. Initialiser le client persistant avec ce chemin
chroma_client = chromadb.PersistentClient(path=str(DATA_DIR))

# get_or_create_collection évite une erreur si la collection existe déjà lors des relances
collection = chroma_client.get_or_create_collection(
    name="rag_collection",
    configuration={"hnsw": {"space": "cosine"}}
)

# Vérifier la communication entre Gemini et ChromaDB

collection.upsert(ids=['id1'], embeddings=[vector], documents=[interaction.output_text])
results = collection.query(query_embeddings=[vector], n_results=1)

print("Chroma_DB")
print(results)
print("Nombre de documents :", collection.count())