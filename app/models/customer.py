from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    rfc = Column(String(13), primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(10))
    country = Column(String(100), default="Mexico")
    
    tier = Column(String(20), default="standard")  # standard, premium, vip
    preferred_language = Column(String(10), default="es")
    communication_preferences = Column(JSON)
    service_preferences = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_interaction = Column(DateTime(timezone=True))
    
    total_bookings = Column(Integer, default=0)
    successful_bookings = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    
    bookings = relationship("Booking", back_populates="customer")
    sessions = relationship("Session", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(rfc='{self.rfc}', phone='{self.phone_number}')>"
    
    @property
    def full_name(self) -> str:
        """Get customer's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"
    
    @property
    def success_rate(self) -> float:
        """Calculate booking success rate"""
        if self.total_bookings == 0:
            return 0.0
        return (self.successful_bookings / self.total_bookings) * 100
