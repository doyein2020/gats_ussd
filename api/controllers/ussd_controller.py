from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import PlainTextResponse
import time
import logging

from ..services.ussd_service import USSDMenuHandler
from ..models.models import USSDSession, USSDLog
from ..main import get_db, verify_api_key, verify_ip
from ..models.schemas import USSDRequest

# Configuration du logger
logger = logging.getLogger(__name__)

# Création du router
router = APIRouter(
    prefix="/ussd",
    tags=["ussd"],
    dependencies=[Depends(verify_api_key), Depends(verify_ip)],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_class=PlainTextResponse)
async def ussd_callback(request: USSDRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal pour les requêtes USSD.
    
    Cette fonction reçoit les requêtes USSD de l'opérateur/agrégateur et les transmet
    au gestionnaire de menus USSD pour traitement.
    
    Args:
        request (USSDRequest): La requête USSD entrante
        db (Session): Session de base de données
        
    Returns:
        PlainTextResponse: Réponse USSD formatée
    """
    start_time = time.time()
    
    logger.info(f"USSD request received: {request.dict()}")
    
    # Traitement de la requête USSD via le gestionnaire de menus
    menu_handler = USSDMenuHandler(db)
    response_text = menu_handler.process_request(
        session_id=request.sessionId,
        phone_number=request.phoneNumber,
        text=request.text,
        service_code=request.serviceCode
    )
    
    end_time = time.time()
    processing_time = (end_time - start_time) * 1000  # en millisecondes
    
    logger.info(f"USSD response sent: {response_text} (processed in {processing_time:.2f}ms)")
    
    return response_text

@router.get("/sessions", dependencies=[Depends(verify_api_key)])
async def get_active_sessions(db: Session = Depends(get_db)):
    """
    Récupère la liste des sessions USSD actives.
    
    Args:
        db (Session): Session de base de données
        
    Returns:
        dict: Liste des sessions actives
    """
    active_sessions = db.query(USSDSession).filter(USSDSession.is_active == True).all()
    
    return {
        "total": len(active_sessions),
        "sessions": [
            {
                "id": session.id,
                "session_id": session.session_id,
                "user_id": session.user_id,
                "started_at": session.started_at,
                "last_activity": session.last_activity,
                "current_menu": session.current_menu
            }
            for session in active_sessions
        ]
    }

@router.get("/logs", dependencies=[Depends(verify_api_key)])
async def get_recent_logs(limit: int = 100, db: Session = Depends(get_db)):
    """
    Récupère les logs récents des interactions USSD.
    
    Args:
        limit (int): Nombre maximum de logs à récupérer
        db (Session): Session de base de données
        
    Returns:
        dict: Liste des logs récents
    """
    recent_logs = db.query(USSDLog).order_by(USSDLog.created_at.desc()).limit(limit).all()
    
    return {
        "total": len(recent_logs),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "session_id": log.session_id,
                "input_text": log.input_text,
                "response_text": log.response_text,
                "menu_level": log.menu_level,
                "created_at": log.created_at,
                "response_time_ms": log.response_time_ms,
                "is_error": log.is_error
            }
            for log in recent_logs
        ]
    }

@router.get("/stats", dependencies=[Depends(verify_api_key)])
async def get_ussd_stats(db: Session = Depends(get_db)):
    """
    Récupère des statistiques sur l'utilisation du service USSD.
    
    Args:
        db (Session): Session de base de données
        
    Returns:
        dict: Statistiques d'utilisation
    """
    # Nombre total de sessions
    total_sessions = db.query(USSDSession).count()
    
    # Nombre de sessions actives
    active_sessions = db.query(USSDSession).filter(USSDSession.is_active == True).count()
    
    # Nombre total d'interactions
    total_interactions = db.query(USSDLog).count()
    
    # Nombre d'erreurs
    error_count = db.query(USSDLog).filter(USSDLog.is_error == True).count()
    
    # Temps de réponse moyen (en millisecondes)
    avg_response_time_query = db.query(
        db.func.avg(USSDLog.response_time_ms)
    ).filter(USSDLog.response_time_ms.isnot(None))
    
    avg_response_time = avg_response_time_query.scalar() or 0
    
    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_interactions": total_interactions,
        "error_count": error_count,
        "error_rate": (error_count / total_interactions) if total_interactions > 0 else 0,
        "avg_response_time_ms": round(avg_response_time, 2)
    }
