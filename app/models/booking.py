from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_rfc = Column(String(13), ForeignKey("customers.rfc"), nullable=False)
    service_id = Column(String(50), ForeignKey("services.id"), nullable=False)
    supplier_id = Column(String(50), ForeignKey("suppliers.id"))
    session_id = Column(String(50), ForeignKey("sessions.id"))
    
    status = Column(String(20), default="pending")  # pending, confirmed, in_progress, completed, cancelled
    priority = Column(String(20), default="normal")  # low, normal, high, emergency
    
    service_parameters = Column(JSON)
    special_instructions = Column(Text)
    estimated_duration_minutes = Column(Integer)
    
    requested_date = Column(DateTime(timezone=True))
    requested_time_slot = Column(String(20))
    confirmed_datetime = Column(DateTime(timezone=True))
    completed_datetime = Column(DateTime(timezone=True))
    
    service_address = Column(Text)
    service_city = Column(String(100))
    service_state = Column(String(100))
    service_postal_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    
    quoted_price = Column(Float)
    final_price = Column(Float)
    currency = Column(String(3), default="MXN")
    payment_status = Column(String(20), default="pending")
    payment_method = Column(String(50))
    
    customer_rating = Column(Integer)  # 1-5 stars
    customer_feedback = Column(Text)
    supplier_rating = Column(Integer)  # 1-5 stars
    supplier_feedback = Column(Text)
    
    supplier_response_time_minutes = Column(Float)
    total_communication_messages = Column(Integer, default=0)
    escalation_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True))
    cancellation_reason = Column(String(200))
    
    customer = relationship("Customer", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    supplier = relationship("Supplier", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id='{self.id}', customer_rfc='{self.customer_rfc}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if booking is in an active state"""
        return self.status in ["pending", "confirmed", "in_progress"]
    
    @property
    def is_completed(self) -> bool:
        """Check if booking is completed"""
        return self.status == "completed"

class BookingHistory(Base):
    __tablename__ = "booking_history"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(50), ForeignKey("bookings.id"), nullable=False)
    
    previous_status = Column(String(20))
    new_status = Column(String(20), nullable=False)
    changed_by = Column(String(100))  # system, customer, supplier, agent
    change_reason = Column(String(200))
    
    notes = Column(Text)
    booking_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BookingHistory(booking_id='{self.booking_id}', status='{self.new_status}')>"
