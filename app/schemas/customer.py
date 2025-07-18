from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class CustomerBase(BaseModel):
    rfc: str = Field(..., min_length=12, max_length=13)
    phone_number: str = Field(..., min_length=10, max_length=20)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Mexico"
    
    tier: str = "standard"
    preferred_language: str = "es"
    communication_preferences: Optional[Dict[str, Any]] = None
    service_preferences: Optional[Dict[str, Any]] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    tier: Optional[str] = None
    preferred_language: Optional[str] = None
    communication_preferences: Optional[Dict[str, Any]] = None
    service_preferences: Optional[Dict[str, Any]] = None

class Customer(CustomerBase):
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_interaction: Optional[datetime]
    total_bookings: int
    successful_bookings: int
    average_rating: float
    total_spent: float
    
    class Config:
        from_attributes = True

class CustomerProfile(BaseModel):
    rfc: str
    full_name: str
    phone_number: str
    email: Optional[str]
    tier: str
    success_rate: float
    total_bookings: int
    average_rating: float
    last_interaction: Optional[datetime]
    is_verified: bool
    
    class Config:
        from_attributes = True
