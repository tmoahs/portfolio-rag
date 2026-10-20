import logging
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.limiter import limiter
from src.api.routes import router
from src.rag.config import ALLOWED_ORIGINS
from src.rag.generation import genai_client
from src.rag.vectorstore import get_collection

# Configuration des logs serveur
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage de l'API : initialisation Chroma et Gemini...")
    _ = get_collection()
    _ = genai_client
    logger.info("Ressources RAG prêtes.")
    yield
    logger.info("Arrêt de l'API.")


app = FastAPI(
    title="Portfolio RAG API",
    description="API de consultation du profil professionnel de Thomas Patout",
    version="0.1.0",
    lifespan=lifespan,
)

# Configuration du Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuration CORS stricte
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Middleware de journalisation
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - Statut: {response.status_code} - Durée: {duration:.3f}s"
    )
    return response


# Inclusion des routes
app.include_router(router)