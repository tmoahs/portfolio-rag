from pathlib import Path
import os

from dotenv import load_dotenv

# Charge .env une seule fois, pour que chaque module (scripts, tests, API) voie
# les mêmes variables. Sans effet dans les conteneurs où l'environnement est
# déjà fourni par Compose.
load_dotenv()

# Dossiers

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = ROOT_DIR / "data"

KNOWLEDGE_DIR = ROOT_DIR / "knowledge"

STATIC_DIR = ROOT_DIR / "static"

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
# Origines autorisées pour CORS (même origine en prod via le proxy).
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000",
).split(",")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Durée de conservation des échanges/questions (en jours).
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "365"))

# Cache de réponses (voir src/rag/cache.py)
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "1") == "1"
CACHE_SEMANTIC = os.getenv("CACHE_SEMANTIC", "1") == "1"
CACHE_SIMILARITY_THRESHOLD = float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.97"))
CACHE_TTL_DAYS = int(os.getenv("CACHE_TTL_DAYS", "7"))
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "500"))

# Limites de requêtes par IP
RATE_LIMIT_ASK = os.getenv("RATE_LIMIT_ASK", "10/minute")
RATE_LIMIT_FEEDBACK = os.getenv("RATE_LIMIT_FEEDBACK", "20/minute")

# Base de données
DATABASE_URL = os.getenv("DATABASE_URL")