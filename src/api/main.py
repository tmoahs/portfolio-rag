import logging
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.limiter import limiter
from src.api.routes import router
from src.rag.config import ALLOWED_ORIGINS
from src.rag.generation import genai_client
from src.rag.vectorstore import get_collection
from src.api.db import close_db_pool, init_db_pool

# Configuration des logs serveur
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage de l'API : initialisation Chroma, Gemini et Postgres...")
    try:
        _ = get_collection()
        _ = genai_client
    except Exception as e:
        logger.warning(f"Ressources RAG indisponibles au démarrage : {e}")
    try:
        await init_db_pool()
    except Exception as e:
        logger.warning(f"Pool Postgres indisponible au démarrage : {e}")
    logger.info("Application prête.")
    yield
    logger.info("Arrêt de l'API : fermeture des connexions...")
    await close_db_pool()

app = FastAPI(
    title="Portfolio RAG API",
    description="API de consultation du profil professionnel de Thomas Patout",
    version="0.1.0",
    lifespan=lifespan,
)

# 1. Fichiers CSS et JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Route principale qui renvoie le fichier HTML
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

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