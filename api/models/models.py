from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class User(Base):
    """
    Modèle pour les utilisateurs du service USSD.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    registered_at = Column(DateTime, default=func.now(), nullable=False)
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relations
    sessions = relationship("USSDSession", back_populates="user")
    logs = relationship("USSDLog", back_populates="user")
    subscriptions = relationship("ServiceSubscription", back_populates="user")

    def __repr__(self):
        return f"<User {self.phone_number}>"


class USSDSession(Base):
    """
    Modèle pour les sessions USSD.
    """
    __tablename__ = "ussd_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_code = Column(String(20), nullable=True)
    current_menu = Column(String(100), nullable=True)
    session_data = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=func.now(), nullable=False)
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now())
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relations
    user = relationship("User", back_populates="sessions")
    logs = relationship("USSDLog", back_populates="session")

    def __repr__(self):
        return f"<USSDSession {self.session_id}>"


class USSDLog(Base):
    """
    Modèle pour les logs des interactions USSD.
    """
    __tablename__ = "ussd_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("ussd_sessions.id"), nullable=False)
    input_text = Column(String(255), nullable=True)
    response_text = Column(Text, nullable=True)
    menu_level = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    is_error = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="logs")
    session = relationship("USSDSession", back_populates="logs")

    def __repr__(self):
        return f"<USSDLog {self.id}>"


class USSDService(Base):
    """
    Modèle pour les services disponibles via USSD.
    """
    __tablename__ = "ussd_services"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    menu_structure = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    subscriptions = relationship("ServiceSubscription", back_populates="service")

    def __repr__(self):
        return f"<USSDService {self.name}>"


class ServiceSubscription(Base):
    """
    Modèle pour les abonnements des utilisateurs aux services.
    """
    __tablename__ = "service_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("ussd_services.id"), nullable=False)
    subscribed_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relations
    user = relationship("User", back_populates="subscriptions")
    service = relationship("USSDService", back_populates="subscriptions")

    def __repr__(self):
        return f"<ServiceSubscription {self.id}>"


class SurveyResponse(Base):
    """
    Modèle pour les réponses aux sondages USSD.
    """
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    survey_id = Column(String(50), nullable=False)
    question_id = Column(String(50), nullable=False)
    response_value = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    user = relationship("User")

    def __repr__(self):
        return f"<SurveyResponse {self.id}>"
