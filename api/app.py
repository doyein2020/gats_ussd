import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import logging
from prometheus_client import make_asgi_app

from controllers.ussd_controller import router as ussd_router
from models.models import Base
from sqlalchemy import create_engine

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DB_USER = os.getenv("DB_USER", "ussd_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "ussd_db")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuration de l'API
API_KEY = os.getenv("API_KEY", "your_secure_api_key")
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "127.0.0.1").split(",")

# Configuration des logs
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ussd_api.log"),
    ],
)
logger = logging.getLogger(__name__)

# Middleware de sécurité
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

def verify_ip(request):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS and "*" not in ALLOWED_IPS:
        logger.warning(f"Unauthorized access attempt from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return client_ip

# Création de l'application FastAPI
app = FastAPI(
    title="USSD Platform API",
    description="API pour la plateforme USSD interne",
    version="1.0.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exposition des métriques Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Enregistrement des routes
app.include_router(ussd_router)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API de la plateforme USSD"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Initialisation de la base de données
def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    logger.info("Base de données initialisée avec succès")

# Point d'entrée pour l'exécution directe
if __name__ == "__main__":
    import uvicorn
    
    # Initialisation de la base de données
    init_db()
    
    # Démarrage du serveur
    uvicorn.run(
        "app:app", 
        host=os.getenv("SERVER_HOST", "0.0.0.0"), 
        port=int(os.getenv("SERVER_PORT", "8000")),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
