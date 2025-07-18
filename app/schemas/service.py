from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ServiceBase(BaseModel):
    id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = None
    
    complexity_level: str = "medium"
    estimated_duration_minutes: Optional[int] = None
    base_price: Optional[float] = None
    price_currency: str = "MXN"
    
    required_parameters: Optional[List[str]] = None
    optional_parameters: Optional[List[str]] = None
    service_keywords: Optional[List[str]] = None
    
    is_active: bool = True
    is_emergency_service: bool = False
    requires_appointment: bool = True
    available_hours: Optional[Dict[str, Any]] = None
    geographic_restrictions: Optional[Dict[str, Any]] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    complexity_level: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    base_price: Optional[float] = None
    is_active: Optional[bool] = None
    is_emergency_service: Optional[bool] = None
    requires_appointment: Optional[bool] = None
    available_hours: Optional[Dict[str, Any]] = None
    geographic_restrictions: Optional[Dict[str, Any]] = None

class Service(ServiceBase):
    created_at: datetime
    updated_at: Optional[datetime]
    total_requests: int
    successful_completions: int
    average_rating: float
    average_response_time_minutes: float
    success_rate: float
    
    class Config:
        from_attributes = True

class ServiceIdentificationRequest(BaseModel):
    message_text: str = Field(..., min_length=1)
    customer_rfc: Optional[str] = None
    conversation_context: Optional[Dict[str, Any]] = None

class ServiceIdentificationResponse(BaseModel):
    identified_service: Optional[Service] = None
    confidence_score: int = Field(..., ge=0, le=100)
    alternative_services: List[Service] = []
    required_parameters: List[str] = []
    missing_parameters: List[str] = []
    clarification_needed: bool = False
    clarification_questions: List[str] = []
