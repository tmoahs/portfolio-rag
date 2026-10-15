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
    contents=interaction.output_text  # On réutilise la sortie ici
)

# Accès au vecteur de nombres
vector = result.embeddings[0].values

print("\n--- Embeddings de la réponse ---")
print(f"Dimension du vecteur : {len(vector)}")
print(f"3 premières valeurs : {vector[:3]}")

# Test ChromaDB
from pathlib import Path
import chromadb

# 1. Remonter d'un cran au-dessus de scripts/ pour atteindre la racine du projet
ROOT_DIR = Path(__file__).resolve().parent.parent

# 2. Pointer vers le dossier data à la racine
CHROMA_PATH = ROOT_DIR / "data"

# 3. Initialiser le client persistant avec ce chemin
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# get_or_create_collection évite une erreur si la collection existe déjà lors des relances
collection = chroma_client.get_or_create_collection(name="my_collection")

print("Chroma_DB")
print("Nombre de documents :", collection.count())