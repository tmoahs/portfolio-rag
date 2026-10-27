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
from src.rag.config import ALLOWED_ORIGINS, STATIC_DIR
from src.rag.generation import genai_client
from src.rag.vectorstore import get_collection
from src.api.db import close_db_pool, init_db_pool
from src.rag.cache import init_cache

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
    # Le pré-chargement des ressources RAG / DB est un confort de dev : s'il échoue
    # (Chroma ou Postgres non démarrés), on continue quand même pour que la partie
    # statique (index.html, /docs) reste accessible. Les routes /ask et /health
    # renverront alors une erreur explicite.
    try:
        _ = get_collection()
        _ = genai_client
    except Exception as e:
        logger.warning(f"Ressources RAG indisponibles au démarrage : {e}")
    try:
        await init_db_pool()
    except Exception as e:
        logger.warning(f"Pool Postgres indisponible au démarrage : {e}")
    try:
        init_cache()
    except Exception as e:
        logger.warning(f"Cache de réponses indisponible : {e}")
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
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 2. Route principale qui renvoie le fichier HTML
@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse(STATIC_DIR / "index.html")


# Page de confidentialité (servie par Caddy en production, par l'API en dev).
@app.get("/confidentialite", include_in_schema=False)
async def read_privacy():
    return FileResponse(STATIC_DIR / "confidentialite.html")


# Sonde de vivacité : ne dépend ni de Postgres ni de Chroma.
@app.get("/live", include_in_schema=False)
async def live():
    return {"status": "ok"}

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


# Inclusion des routes.
#   /api/*  : chemin public (site + reverse proxy, même origine).
#   sans préfixe : conservé pour les scripts (smoke test, eval) et la compatibilité.
app.include_router(router, prefix="/api")
app.include_router(router, include_in_schema=False)