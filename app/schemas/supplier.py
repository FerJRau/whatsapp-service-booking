from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class SupplierBase(BaseModel):
    id: str
    business_name: str = Field(..., min_length=1, max_length=200)
    contact_name: Optional[str] = None
    phone_number: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    whatsapp_number: Optional[str] = None
    
    business_type: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Mexico"
    service_radius_km: float = 25.0
    service_areas: Optional[List[str]] = None
    
    services_offered: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    
    is_active: bool = True
    is_verified: bool = False
    is_premium_partner: bool = False
    operating_hours: Optional[Dict[str, Any]] = None
    max_concurrent_jobs: int = 5
    
    base_rate: Optional[float] = None
    rate_currency: str = "MXN"
    payment_terms: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    whatsapp_number: Optional[str] = None
    business_type: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    service_radius_km: Optional[float] = None
    service_areas: Optional[List[str]] = None
    services_offered: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    operating_hours: Optional[Dict[str, Any]] = None
    max_concurrent_jobs: Optional[int] = None
    base_rate: Optional[float] = None
    payment_terms: Optional[str] = None

class Supplier(SupplierBase):
    current_active_jobs: int
    total_jobs_completed: int
    total_jobs_assigned: int
    average_rating: float
    average_response_time_minutes: float
    completion_rate: float
    customer_satisfaction_score: float
    created_at: datetime
    updated_at: Optional[datetime]
    last_active: Optional[datetime]
    success_rate: float
    is_available: bool
    
    class Config:
        from_attributes = True

class SupplierMatchRequest(BaseModel):
    service_id: str
    customer_location: Optional[Dict[str, float]] = None  # lat, lng
    service_parameters: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    max_suppliers: int = 5

class SupplierMatchResponse(BaseModel):
    matched_suppliers: List[Supplier]
    match_criteria: Dict[str, Any]
    total_available: int
