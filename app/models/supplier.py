from sqlalchemy import Column, String, Text, Boolean, Integer, Float, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(String(50), primary_key=True)
    business_name = Column(String(200), nullable=False)
    contact_name = Column(String(200))
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255))
    whatsapp_number = Column(String(20))
    
    business_type = Column(String(100))
    registration_number = Column(String(100))
    tax_id = Column(String(50))
    
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(10))
    country = Column(String(100), default="Mexico")
    service_radius_km = Column(Float, default=25.0)
    service_areas = Column(JSON)  # List of service areas/zones
    
    services_offered = Column(JSON)  # List of service IDs
    specializations = Column(JSON)  # Areas of expertise
    certifications = Column(JSON)  # Professional certifications
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium_partner = Column(Boolean, default=False)
    operating_hours = Column(JSON)
    max_concurrent_jobs = Column(Integer, default=5)
    current_active_jobs = Column(Integer, default=0)
    
    total_jobs_completed = Column(Integer, default=0)
    total_jobs_assigned = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    average_response_time_minutes = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    customer_satisfaction_score = Column(Float, default=0.0)
    
    base_rate = Column(Float)
    rate_currency = Column(String(3), default="MXN")
    payment_terms = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True))
    
    bookings = relationship("Booking", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier(id='{self.id}', name='{self.business_name}')>"
    
    @property
    def success_rate(self) -> float:
        """Calculate job completion success rate"""
        if self.total_jobs_assigned == 0:
            return 0.0
        return (self.total_jobs_completed / self.total_jobs_assigned) * 100
    
    @property
    def is_available(self) -> bool:
        """Check if supplier is currently available"""
        return (
            self.is_active and 
            self.is_verified and 
            self.current_active_jobs < self.max_concurrent_jobs
        )

class SupplierPerformance(Base):
    __tablename__ = "supplier_performance"
    
    id = Column(String(50), primary_key=True)
    supplier_id = Column(String(50), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    jobs_assigned = Column(Integer, default=0)
    jobs_completed = Column(Integer, default=0)
    jobs_cancelled = Column(Integer, default=0)
    average_response_time_minutes = Column(Float, default=0.0)
    average_completion_time_minutes = Column(Float, default=0.0)
    customer_ratings_received = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    total_revenue = Column(Float, default=0.0)
    revenue_currency = Column(String(3), default="MXN")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SupplierPerformance(supplier_id='{self.supplier_id}', date='{self.date}')>"
