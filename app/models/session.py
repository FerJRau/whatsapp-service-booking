from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_rfc = Column(String(13), nullable=False)
    phone_number = Column(String(20), nullable=False)
    
    status = Column(String(20), default="active")  # active, completed, expired, escalated
    current_step = Column(String(50))
    conversation_context = Column(JSON)
    collected_parameters = Column(JSON)
    
    identified_service_id = Column(String(50))
    service_confidence_score = Column(Integer, default=0)  # 0-100
    service_identification_attempts = Column(Integer, default=0)
    
    total_messages = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True))
    last_message_content = Column(Text)
    
    escalation_reason = Column(String(100))
    escalated_at = Column(DateTime(timezone=True))
    escalated_to = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    customer = relationship("Customer", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
    
    def __repr__(self):
        return f"<Session(id='{self.id}', customer_rfc='{self.customer_rfc}', status='{self.status}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if not self.expires_at:
            return False
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == "active" and not self.is_expired

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(50), nullable=False)
    whatsapp_message_id = Column(String(100))
    
    direction = Column(String(10), nullable=False)  # inbound, outbound
    message_type = Column(String(20), default="text")  # text, image, document, etc.
    content = Column(Text)
    media_url = Column(String(500))
    
    processed = Column(Boolean, default=False)
    processing_time_ms = Column(Integer)
    ai_analysis = Column(JSON)
    extracted_entities = Column(JSON)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    session = relationship("Session", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id='{self.id}', direction='{self.direction}', type='{self.message_type}')>"
