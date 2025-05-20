from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging

from ..models.models import User, USSDSession, USSDLog, USSDService, ServiceSubscription, SurveyResponse

logger = logging.getLogger(__name__)

class USSDSessionManager:
    """
    Gestionnaire de sessions USSD.
    
    Cette classe gère la création, la récupération et la mise à jour des sessions USSD.
    """
    
    @staticmethod
    def get_or_create_session(db: Session, session_id: str, phone_number: str, service_code: Optional[str] = None) -> Tuple[USSDSession, bool]:
        """
        Récupère une session existante ou en crée une nouvelle.
        
        Args:
            db (Session): Session de base de données
            session_id (str): Identifiant de session USSD
            phone_number (str): Numéro de téléphone de l'utilisateur
            service_code (str, optional): Code du service USSD
            
        Returns:
            Tuple[USSDSession, bool]: Session USSD et un booléen indiquant si la session a été créée
        """
        # Vérifier si la session existe déjà
        session = db.query(USSDSession).filter(USSDSession.session_id == session_id).first()
        
        if session:
            # Mettre à jour l'activité de la session
            session.last_activity = datetime.now()
            db.commit()
            return session, False
        
        # Récupérer ou créer l'utilisateur
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Créer une nouvelle session
        session = USSDSession(
            session_id=session_id,
            user_id=user.id,
            service_code=service_code,
            current_menu="main",
            session_data={},
            is_active=True
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session, True
    
    @staticmethod
    def update_session_data(db: Session, session: USSDSession, data: Dict[str, Any]) -> USSDSession:
        """
        Met à jour les données de session.
        
        Args:
            db (Session): Session de base de données
            session (USSDSession): Session USSD à mettre à jour
            data (Dict[str, Any]): Nouvelles données à ajouter/mettre à jour
            
        Returns:
            USSDSession: Session USSD mise à jour
        """
        # Fusionner les données existantes avec les nouvelles données
        current_data = session.session_data or {}
        current_data.update(data)
        
        # Mettre à jour la session
        session.session_data = current_data
        session.last_activity = datetime.now()
        
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def end_session(db: Session, session: USSDSession) -> USSDSession:
        """
        Termine une session USSD.
        
        Args:
            db (Session): Session de base de données
            session (USSDSession): Session USSD à terminer
            
        Returns:
            USSDSession: Session USSD terminée
        """
        session.is_active = False
        session.ended_at = datetime.now()
        
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def log_interaction(
        db: Session, 
        session: USSDSession, 
        input_text: str, 
        response_text: str,
        menu_level: str,
        response_time_ms: Optional[int] = None,
        is_error: bool = False,
        error_message: Optional[str] = None
    ) -> USSDLog:
        """
        Enregistre une interaction USSD dans les logs.
        
        Args:
            db (Session): Session de base de données
            session (USSDSession): Session USSD
            input_text (str): Texte d'entrée de l'utilisateur
            response_text (str): Texte de réponse du système
            menu_level (str): Niveau de menu actuel
            response_time_ms (int, optional): Temps de réponse en millisecondes
            is_error (bool): Indique si une erreur s'est produite
            error_message (str, optional): Message d'erreur éventuel
            
        Returns:
            USSDLog: Log d'interaction créé
        """
        log = USSDLog(
            user_id=session.user_id,
            session_id=session.id,
            input_text=input_text,
            response_text=response_text,
            menu_level=menu_level,
            response_time_ms=response_time_ms,
            is_error=is_error,
            error_message=error_message
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log


class USSDMenuHandler:
    """
    Gestionnaire de menus USSD.
    
    Cette classe traite les requêtes USSD et génère les réponses appropriées
    en fonction du menu actuel et de l'entrée de l'utilisateur.
    """
    
    def __init__(self, db: Session):
        """
        Initialise le gestionnaire de menus USSD.
        
        Args:
            db (Session): Session de base de données
        """
        self.db = db
        self.session_manager = USSDSessionManager()
    
    def process_request(self, session_id: str, phone_number: str, text: str, service_code: Optional[str] = None) -> str:
        """
        Traite une requête USSD et génère la réponse appropriée.
        
        Args:
            session_id (str): Identifiant de session USSD
            phone_number (str): Numéro de téléphone de l'utilisateur
            text (str): Texte de la requête USSD
            service_code (str, optional): Code du service USSD
            
        Returns:
            str: Réponse USSD formatée
        """
        start_time = datetime.now()
        
        try:
            # Récupérer ou créer la session
            session, is_new_session = self.session_manager.get_or_create_session(
                self.db, session_id, phone_number, service_code
            )
            
            # Déterminer le menu et traiter la requête
            if is_new_session or text == "":
                # Afficher le menu principal pour une nouvelle session
                response = self._get_main_menu()
                menu_level = "main"
            else:
                # Traiter l'entrée de l'utilisateur en fonction du menu actuel
                response, menu_level = self._process_menu_input(session, text)
            
            # Calculer le temps de réponse
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Enregistrer l'interaction dans les logs
            self.session_manager.log_interaction(
                self.db, session, text, response, menu_level, response_time_ms
            )
            
            # Si la réponse commence par "END", terminer la session
            if response.startswith("END"):
                self.session_manager.end_session(self.db, session)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing USSD request: {str(e)}")
            
            # Calculer le temps de réponse en cas d'erreur
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Récupérer la session si possible
            try:
                session, _ = self.session_manager.get_or_create_session(
                    self.db, session_id, phone_number, service_code
                )
                
                # Enregistrer l'erreur dans les logs
                self.session_manager.log_interaction(
                    self.db, session, text, "END Une erreur s'est produite. Veuillez réessayer.",
                    "error", response_time_ms, True, str(e)
                )
                
                # Terminer la session en cas d'erreur
                self.session_manager.end_session(self.db, session)
                
            except Exception as inner_e:
                logger.error(f"Error handling error: {str(inner_e)}")
            
            # Renvoyer un message d'erreur générique
            return "END Une erreur s'est produite. Veuillez réessayer."
    
    def _get_main_menu(self) -> str:
        """
        Génère le menu principal USSD.
        
        Returns:
            str: Menu principal formaté
        """
        return "CON Bienvenue sur notre service USSD\n1. Consultation de solde\n2. S'inscrire aux services\n3. Suivi de commande\n4. Sondages"
    
    def _process_menu_input(self, session: USSDSession, text: str) -> Tuple[str, str]:
        """
        Traite l'entrée de l'utilisateur en fonction du menu actuel.
        
        Args:
            session (USSDSession): Session USSD
            text (str): Texte de la requête USSD
            
        Returns:
            Tuple[str, str]: Réponse USSD formatée et niveau de menu
        """
        # Récupérer le menu actuel et les données de session
        current_menu = session.current_menu
        session_data = session.session_data or {}
        
        # Traiter en fonction du texte et du menu actuel
        if text == "1":
            # Consultation de solde
            return self._handle_balance_inquiry(session), "balance"
        
        elif text == "2":
            # Menu d'inscription aux services
            return self._handle_service_subscription_menu(), "services"
        
        elif text.startswith("2*"):
            # Traitement de l'inscription à un service
            parts = text.split("*")
            if len(parts) == 2:
                service_choice = parts[1]
                return self._handle_service_subscription(session, service_choice), "service_subscription"
            else:
                return "END Option non reconnue. Veuillez réessayer.", "error"
        
        elif text == "3":
            # Menu de suivi de commande
            return "CON Entrez votre numéro de commande:", "order_tracking"
        
        elif text.startswith("3*"):
            # Traitement du suivi de commande
            parts = text.split("*")
            if len(parts) == 2:
                order_number = parts[1]
                return self._handle_order_tracking(session, order_number), "order_result"
            else:
                return "END Option non reconnue. Veuillez réessayer.", "error"
        
        elif text == "4":
            # Menu de sondage
            return self._handle_survey_menu(), "survey"
        
        elif text.startswith("4*"):
            # Traitement de la réponse au sondage
            parts = text.split("*")
            if len(parts) == 2:
                survey_response = parts[1]
                return self._handle_survey_response(session, survey_response), "survey_response"
            else:
                return "END Option non reconnue. Veuillez réessayer.", "error"
        
        else:
            # Option non reconnue
            return "END Option non reconnue. Veuillez réessayer.", "error"
    
    def _handle_balance_inquiry(self, session: USSDSession) -> str:
        """
        Traite une demande de consultation de solde.
        
        Args:
            session (USSDSession): Session USSD
            
        Returns:
            str: Réponse USSD formatée
        """
        # Dans un système réel, vous récupéreriez le solde depuis une base de données ou un service externe
        # Ici, nous utilisons une valeur simulée
        balance = 10000
        
        # Mettre à jour les données de session
        self.session_manager.update_session_data(self.db, session, {"last_balance_check": datetime.now().isoformat()})
        
        return f"END Votre solde est de {balance} FCFA"
    
    def _handle_service_subscription_menu(self) -> str:
        """
        Génère le menu d'inscription aux services.
        
        Returns:
            str: Menu d'inscription formaté
        """
        # Dans un système réel, vous récupéreriez la liste des services depuis la base de données
        return "CON Choisissez un service:\n1. Service A\n2. Service B\n3. Service C"
    
    def _handle_service_subscription(self, session: USSDSession, service_choice: str) -> str:
        """
        Traite une demande d'inscription à un service.
        
        Args:
            session (USSDSession): Session USSD
            service_choice (str): Choix de service
            
        Returns:
            str: Réponse USSD formatée
        """
        # Mapper le choix à un service
        service_map = {
            "1": "Service A",
            "2": "Service B",
            "3": "Service C"
        }
        
        service_name = service_map.get(service_choice)
        
        if not service_name:
            return "END Service non reconnu. Veuillez réessayer."
        
        # Dans un système réel, vous enregistreriez l'abonnement dans la base de données
        # Mettre à jour les données de session
        self.session_manager.update_session_data(
            self.db, 
            session, 
            {
                "subscribed_service": service_name,
                "subscription_date": datetime.now().isoformat()
            }
        )
        
        return f"END Vous êtes maintenant inscrit au {service_name}. Merci!"
    
    def _handle_order_tracking(self, session: USSDSession, order_number: str) -> str:
        """
        Traite une demande de suivi de commande.
        
        Args:
            session (USSDSession): Session USSD
            order_number (str): Numéro de commande
            
        Returns:
            str: Réponse USSD formatée
        """
        # Dans un système réel, vous récupéreriez le statut de la commande depuis une base de données ou un service externe
        # Ici, nous utilisons un statut simulé
        
        # Mettre à jour les données de session
        self.session_manager.update_session_data(
            self.db, 
            session, 
            {
                "tracked_order": order_number,
                "tracking_date": datetime.now().isoformat()
            }
        )
        
        return f"END Votre commande {order_number} est en cours de livraison."
    
    def _handle_survey_menu(self) -> str:
        """
        Génère le menu de sondage.
        
        Returns:
            str: Menu de sondage formaté
        """
        return "CON Participez à notre sondage:\nÊtes-vous satisfait de nos services?\n1. Très satisfait\n2. Satisfait\n3. Peu satisfait"
    
    def _handle_survey_response(self, session: USSDSession, response_choice: str) -> str:
        """
        Traite une réponse à un sondage.
        
        Args:
            session (USSDSession): Session USSD
            response_choice (str): Choix de réponse
            
        Returns:
            str: Réponse USSD formatée
        """
        # Mapper le choix à une réponse
        response_map = {
            "1": "Très satisfait",
            "2": "Satisfait",
            "3": "Peu satisfait"
        }
        
        response_value = response_map.get(response_choice)
        
        if not response_value:
            return "END Réponse non reconnue. Veuillez réessayer."
        
        # Dans un système réel, vous enregistreriez la réponse dans la base de données
        survey_response = SurveyResponse(
            user_id=session.user_id,
            survey_id="satisfaction_survey",
            question_id="general_satisfaction",
            response_value=response_value
        )
        
        self.db.add(survey_response)
        self.db.commit()
        
        # Mettre à jour les données de session
        self.session_manager.update_session_data(
            self.db, 
            session, 
            {
                "survey_response": response_value,
                "survey_date": datetime.now().isoformat()
            }
        )
        
        return "END Merci pour votre participation au sondage!"
