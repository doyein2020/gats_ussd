from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

# Schémas pour les requêtes USSD
class USSDRequest(BaseModel):
    sessionId: str = Field(..., description="Identifiant unique de la session USSD")
    phoneNumber: str = Field(..., description="Numéro de téléphone de l'utilisateur")
    text: str = Field(..., description="Texte de la requête USSD")
    serviceCode: Optional[str] = Field(None, description="Code du service USSD")

# Schémas pour les utilisateurs
class UserBase(BaseModel):
    phone_number: str = Field(..., description="Numéro de téléphone de l'utilisateur")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    registered_at: datetime
    last_activity: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

# Schémas pour les sessions USSD
class USSDSessionBase(BaseModel):
    session_id: str = Field(..., description="Identifiant unique de la session USSD")
    user_id: int = Field(..., description="ID de l'utilisateur")
    service_code: Optional[str] = None
    current_menu: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None
    is_active: bool = True

class USSDSessionCreate(USSDSessionBase):
    pass

class USSDSessionUpdate(BaseModel):
    current_menu: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    ended_at: Optional[datetime] = None

class USSDSessionInDB(USSDSessionBase):
    id: int
    started_at: datetime
    last_activity: datetime
    ended_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class USSDSession(USSDSessionInDB):
    pass

# Schémas pour les logs USSD
class USSDLogBase(BaseModel):
    user_id: int = Field(..., description="ID de l'utilisateur")
    session_id: int = Field(..., description="ID de la session USSD")
    input_text: Optional[str] = None
    response_text: Optional[str] = None
    menu_level: Optional[str] = None
    response_time_ms: Optional[int] = None
    is_error: bool = False
    error_message: Optional[str] = None

class USSDLogCreate(USSDLogBase):
    pass

class USSDLogInDB(USSDLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class USSDLog(USSDLogInDB):
    pass

# Schémas pour les services USSD
class USSDServiceBase(BaseModel):
    code: str = Field(..., description="Code unique du service USSD")
    name: str = Field(..., description="Nom du service")
    description: Optional[str] = None
    menu_structure: Dict[str, Any] = Field(..., description="Structure des menus du service")
    is_active: bool = True

class USSDServiceCreate(USSDServiceBase):
    pass

class USSDServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    menu_structure: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class USSDServiceInDB(USSDServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class USSDService(USSDServiceInDB):
    pass

# Schémas pour les abonnements aux services
class ServiceSubscriptionBase(BaseModel):
    user_id: int = Field(..., description="ID de l'utilisateur")
    service_id: int = Field(..., description="ID du service")
    is_active: bool = True
    expires_at: Optional[datetime] = None

class ServiceSubscriptionCreate(ServiceSubscriptionBase):
    pass

class ServiceSubscriptionUpdate(BaseModel):
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class ServiceSubscriptionInDB(ServiceSubscriptionBase):
    id: int
    subscribed_at: datetime

    class Config:
        orm_mode = True

class ServiceSubscription(ServiceSubscriptionInDB):
    pass

# Schémas pour les réponses aux sondages
class SurveyResponseBase(BaseModel):
    user_id: int = Field(..., description="ID de l'utilisateur")
    survey_id: str = Field(..., description="ID du sondage")
    question_id: str = Field(..., description="ID de la question")
    response_value: str = Field(..., description="Valeur de la réponse")

class SurveyResponseCreate(SurveyResponseBase):
    pass

class SurveyResponseInDB(SurveyResponseBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SurveyResponse(SurveyResponseInDB):
    pass

# Schémas pour les statistiques
class USSDStats(BaseModel):
    total_sessions: int
    active_sessions: int
    total_interactions: int
    error_count: int
    error_rate: float
    avg_response_time_ms: float
