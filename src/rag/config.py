from pathlib import Path
import os

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

# Pour la génération

TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 1200
DISTANCE_THRESHOLD = 0.40

# Sécurité & API
# Origines autorisées pour CORS (localhost pour le dev, adaptable via .env)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:8000",
).split(",")

# Limites de requêtes par IP
RATE_LIMIT_ASK = os.getenv("RATE_LIMIT_ASK", "10/minute")
RATE_LIMIT_FEEDBACK = os.getenv("RATE_LIMIT_FEEDBACK", "20/minute")

# Base de données
DATABASE_URL = os.getenv("DATABASE_URL")