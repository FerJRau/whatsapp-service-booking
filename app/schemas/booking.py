from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class BookingBase(BaseModel):
    customer_rfc: str = Field(..., min_length=12, max_length=13)
    service_id: str
    supplier_id: Optional[str] = None
    session_id: Optional[str] = None
    
    priority: str = "normal"
    service_parameters: Optional[Dict[str, Any]] = None
    special_instructions: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    
    requested_date: Optional[datetime] = None
    requested_time_slot: Optional[str] = None
    
    service_address: Optional[str] = None
    service_city: Optional[str] = None
    service_state: Optional[str] = None
    service_postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    quoted_price: Optional[float] = None
    currency: str = "MXN"
    payment_method: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    supplier_id: Optional[str] = None
    confirmed_datetime: Optional[datetime] = None
    final_price: Optional[float] = None
    payment_status: Optional[str] = None
    customer_rating: Optional[int] = Field(None, ge=1, le=5)
    customer_feedback: Optional[str] = None
    supplier_rating: Optional[int] = Field(None, ge=1, le=5)
    supplier_feedback: Optional[str] = None
    cancellation_reason: Optional[str] = None

class Booking(BookingBase):
    id: str
    status: str
    confirmed_datetime: Optional[datetime]
    completed_datetime: Optional[datetime]
    final_price: Optional[float]
    payment_status: str
    customer_rating: Optional[int]
    customer_feedback: Optional[str]
    supplier_rating: Optional[int]
    supplier_feedback: Optional[str]
    supplier_response_time_minutes: Optional[float]
    total_communication_messages: int
    escalation_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    is_active: bool
    is_completed: bool
    
    class Config:
        from_attributes = True

class BookingStatusUpdate(BaseModel):
    booking_id: str
    new_status: str
    changed_by: str
    change_reason: Optional[str] = None
    notes: Optional[str] = None
