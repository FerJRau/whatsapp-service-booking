from sqlalchemy import Column, String, Text, Boolean, Integer, Float, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Service(Base):
    __tablename__ = "services"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    
    complexity_level = Column(String(20), default="medium")  # low, medium, high
    estimated_duration_minutes = Column(Integer)
    base_price = Column(Float)
    price_currency = Column(String(3), default="MXN")
    
    required_parameters = Column(JSON)  # List of required parameters
    optional_parameters = Column(JSON)  # List of optional parameters
    service_keywords = Column(JSON)  # Keywords for service identification
    
    is_active = Column(Boolean, default=True)
    is_emergency_service = Column(Boolean, default=False)
    requires_appointment = Column(Boolean, default=True)
    available_hours = Column(JSON)  # Operating hours
    geographic_restrictions = Column(JSON)  # Service area restrictions
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    total_requests = Column(Integer, default=0)
    successful_completions = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    average_response_time_minutes = Column(Float, default=0.0)
    
    bookings = relationship("Booking", back_populates="service")
    
    def __repr__(self):
        return f"<Service(id='{self.id}', name='{self.name}')>"
    
    @property
    def success_rate(self) -> float:
        """Calculate service completion success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_completions / self.total_requests) * 100

class ServiceParameter(Base):
    __tablename__ = "service_parameters"
    
    id = Column(String(50), primary_key=True)
    service_id = Column(String(50), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    parameter_type = Column(String(50), nullable=False)  # text, number, date, selection, boolean
    is_required = Column(Boolean, default=False)
    validation_rules = Column(JSON)
    default_value = Column(String(255))
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ServiceParameter(id='{self.id}', name='{self.parameter_name}')>"
