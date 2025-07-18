from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class SessionBase(BaseModel):
    customer_rfc: str = Field(..., min_length=12, max_length=13)
    phone_number: str = Field(..., min_length=10, max_length=20)

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    status: Optional[str] = None
    current_step: Optional[str] = None
    conversation_context: Optional[Dict[str, Any]] = None
    collected_parameters: Optional[Dict[str, Any]] = None
    identified_service_id: Optional[str] = None
    service_confidence_score: Optional[int] = Field(None, ge=0, le=100)
    escalation_reason: Optional[str] = None
    escalated_to: Optional[str] = None

class Session(SessionBase):
    id: str
    status: str
    current_step: Optional[str]
    conversation_context: Optional[Dict[str, Any]]
    collected_parameters: Optional[Dict[str, Any]]
    identified_service_id: Optional[str]
    service_confidence_score: int
    service_identification_attempts: int
    total_messages: int
    last_message_at: Optional[datetime]
    last_message_content: Optional[str]
    escalation_reason: Optional[str]
    escalated_at: Optional[datetime]
    escalated_to: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_expired: bool
    is_active: bool
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    session_id: str
    direction: str = Field(..., regex="^(inbound|outbound)$")
    message_type: str = "text"
    content: Optional[str] = None
    media_url: Optional[str] = None

class MessageCreate(MessageBase):
    whatsapp_message_id: Optional[str] = None

class Message(MessageBase):
    id: str
    whatsapp_message_id: Optional[str]
    processed: bool
    processing_time_ms: Optional[int]
    ai_analysis: Optional[Dict[str, Any]]
    extracted_entities: Optional[Dict[str, Any]]
    timestamp: datetime
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True
