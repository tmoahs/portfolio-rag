from pathlib import Path

# Dossiers

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = ROOT_DIR / "data"

KNOWLEDGE_DIR = ROOT_DIR / "knowledge"

# Modèles

LLM_MODEL = "gemini-3.8-flash"
EMBEDDING_MODEL = "gemini-embedding-2"

# Taille des chunks

CHUNK_SIZE = 500

# Top K

TOP_K = 4