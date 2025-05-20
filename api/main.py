import os
from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response, PlainTextResponse

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

# Configuration de la base de données
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ussd_api.log"),
    ],
)
logger = logging.getLogger(__name__)

# Métriques Prometheus
ussd_requests_total = Counter(
    "ussd_requests_total", "Total number of USSD requests", ["session_type"]
)
ussd_response_time = Histogram(
    "ussd_response_time_seconds", "USSD response time in seconds"
)

# Modèles Pydantic
class USSDRequest(BaseModel):
    sessionId: str
    phoneNumber: str
    text: str
    serviceCode: Optional[str] = None

# Middleware de sécurité
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

def verify_ip(request: Request):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS and "*" not in ALLOWED_IPS:
        logger.warning(f"Unauthorized access attempt from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return client_ip

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Routes
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API de la plateforme USSD"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")

@app.post("/ussd", dependencies=[Depends(verify_api_key), Depends(verify_ip)])
async def ussd_callback(request: USSDRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal pour les requêtes USSD.
    
    Cette fonction traite les requêtes USSD entrantes et renvoie les réponses appropriées.
    
    Args:
        request (USSDRequest): La requête USSD entrante
        db (Session): Session de base de données
        
    Returns:
        PlainTextResponse: Réponse USSD formatée
    """
    logger.info(f"USSD request received: {request.dict()}")
    
    # Incrémentation du compteur de requêtes
    is_initial = request.text == ""
    session_type = "initial" if is_initial else "continuation"
    ussd_requests_total.labels(session_type=session_type).inc()
    
    # Mesure du temps de réponse
    with ussd_response_time.time():
        # Traitement de la requête USSD
        response_text = process_ussd_request(request, db)
    
    logger.info(f"USSD response: {response_text}")
    
    # Renvoyer la réponse au format texte brut
    return PlainTextResponse(content=response_text)

def process_ussd_request(request: USSDRequest, db: Session) -> str:
    """
    Traite une requête USSD et génère la réponse appropriée.
    
    Args:
        request (USSDRequest): La requête USSD
        db (Session): Session de base de données
        
    Returns:
        str: Réponse USSD formatée
    """
    session_id = request.sessionId
    phone_number = request.phoneNumber
    text = request.text
    
    # Si c'est la première requête (texte vide), afficher le menu principal
    if text == "":
        return "CON Bienvenue sur notre service USSD\n1. Consultation de solde\n2. S'inscrire aux services\n3. Suivi de commande\n4. Sondages"
    
    # Traitement des menus et sous-menus
    if text == "1":
        # Consultation de solde - Simulé pour l'exemple
        return "END Votre solde est de 10 000 FCFA"
    
    elif text == "2":
        return "CON Choisissez un service:\n1. Service A\n2. Service B\n3. Service C"
    
    elif text.startswith("2*"):
        service = text.split("*")[1]
        return f"END Vous êtes maintenant inscrit au service {service}. Merci!"
    
    elif text == "3":
        return "CON Entrez votre numéro de commande:"
    
    elif text.startswith("3*"):
        order_number = text.split("*")[1]
        # Ici, vous feriez une requête à la base de données pour obtenir le statut réel
        return f"END Votre commande {order_number} est en cours de livraison."
    
    elif text == "4":
        return "CON Participez à notre sondage:\nÊtes-vous satisfait de nos services?\n1. Très satisfait\n2. Satisfait\n3. Peu satisfait"
    
    elif text.startswith("4*"):
        rating = text.split("*")[1]
        # Enregistrer la réponse dans la base de données
        return "END Merci pour votre participation au sondage!"
    
    else:
        return "END Option non reconnue. Veuillez réessayer."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
