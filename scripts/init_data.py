#!/usr/bin/env python3
"""
Initialize database with sample data for testing
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import AsyncSessionLocal, engine, Base
from app.models.customer import Customer
from app.models.service import Service
from app.models.supplier import Supplier
from datetime import datetime

async def init_database():
    """Initialize database with sample data"""
    
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        print("Adding sample services...")
        
        services = [
            Service(
                id="plumbing_repair",
                name="Reparación de Plomería",
                description="Servicios de reparación de plomería residencial y comercial",
                category="hogar",
                subcategory="plomería",
                complexity_level="medium",
                estimated_duration_minutes=120,
                base_price=500.0,
                required_parameters=["location", "problem_description"],
                optional_parameters=["preferred_time", "urgency"],
                service_keywords=["plomería", "tubería", "fuga", "agua", "baño", "cocina"],
                is_active=True,
                requires_appointment=True
            ),
            Service(
                id="electrical_repair",
                name="Reparación Eléctrica",
                description="Servicios de reparación e instalación eléctrica",
                category="hogar",
                subcategory="electricidad",
                complexity_level="high",
                estimated_duration_minutes=180,
                base_price=800.0,
                required_parameters=["location", "electrical_issue"],
                optional_parameters=["preferred_time", "emergency"],
                service_keywords=["electricidad", "luz", "apagón", "instalación", "cables"],
                is_active=True,
                requires_appointment=True
            ),
            Service(
                id="cleaning_service",
                name="Servicio de Limpieza",
                description="Limpieza residencial y comercial",
                category="hogar",
                subcategory="limpieza",
                complexity_level="low",
                estimated_duration_minutes=240,
                base_price=300.0,
                required_parameters=["location", "property_size"],
                optional_parameters=["cleaning_type", "frequency"],
                service_keywords=["limpieza", "aseo", "casa", "oficina", "profunda"],
                is_active=True,
                requires_appointment=True
            )
        ]
        
        for service in services:
            session.add(service)
        
        print("Adding sample suppliers...")
        
        suppliers = [
            Supplier(
                id="plumber_juan",
                business_name="Plomería Juan Pérez",
                contact_name="Juan Pérez",
                phone_number="+525512345678",
                email="juan@plomeria.com",
                whatsapp_number="+525512345678",
                business_type="individual",
                city="Ciudad de México",
                state="CDMX",
                country="Mexico",
                service_radius_km=30.0,
                services_offered=["plumbing_repair"],
                specializations=["residential_plumbing", "emergency_repairs"],
                is_active=True,
                is_verified=True,
                operating_hours={"monday": "8:00-18:00", "tuesday": "8:00-18:00"},
                max_concurrent_jobs=3,
                base_rate=500.0,
                average_rating=4.5,
                total_jobs_completed=150,
                total_jobs_assigned=160,
                completion_rate=93.75
            ),
            Supplier(
                id="electrician_maria",
                business_name="Electricidad María González",
                contact_name="María González",
                phone_number="+525587654321",
                email="maria@electricidad.com",
                whatsapp_number="+525587654321",
                business_type="individual",
                city="Ciudad de México",
                state="CDMX",
                country="Mexico",
                service_radius_km=25.0,
                services_offered=["electrical_repair"],
                specializations=["residential_electrical", "commercial_electrical"],
                is_active=True,
                is_verified=True,
                is_premium_partner=True,
                operating_hours={"monday": "7:00-19:00", "tuesday": "7:00-19:00"},
                max_concurrent_jobs=2,
                base_rate=800.0,
                average_rating=4.8,
                total_jobs_completed=200,
                total_jobs_assigned=205,
                completion_rate=97.56
            ),
            Supplier(
                id="cleaning_company",
                business_name="Limpieza Profesional SA",
                contact_name="Carlos Rodríguez",
                phone_number="+525555555555",
                email="info@limpiezapro.com",
                whatsapp_number="+525555555555",
                business_type="company",
                city="Ciudad de México",
                state="CDMX",
                country="Mexico",
                service_radius_km=40.0,
                services_offered=["cleaning_service"],
                specializations=["residential_cleaning", "commercial_cleaning", "deep_cleaning"],
                is_active=True,
                is_verified=True,
                operating_hours={"monday": "6:00-20:00", "tuesday": "6:00-20:00"},
                max_concurrent_jobs=10,
                base_rate=300.0,
                average_rating=4.3,
                total_jobs_completed=500,
                total_jobs_assigned=520,
                completion_rate=96.15
            )
        ]
        
        for supplier in suppliers:
            session.add(supplier)
        
        print("Adding sample customers...")
        
        customers = [
            Customer(
                rfc="ABCD123456EF1",
                phone_number="+525511111111",
                first_name="Ana",
                last_name="López",
                email="ana.lopez@email.com",
                street_address="Av. Reforma 123",
                city="Ciudad de México",
                state="CDMX",
                postal_code="06600",
                tier="premium",
                preferred_language="es",
                is_active=True,
                is_verified=True,
                total_bookings=5,
                successful_bookings=5,
                average_rating=4.8,
                created_at=datetime.utcnow()
            ),
            Customer(
                rfc="EFGH789012IJ3",
                phone_number="+525522222222",
                first_name="Carlos",
                last_name="Martínez",
                email="carlos.martinez@email.com",
                street_address="Calle Insurgentes 456",
                city="Ciudad de México",
                state="CDMX",
                postal_code="03100",
                tier="standard",
                preferred_language="es",
                is_active=True,
                is_verified=True,
                total_bookings=2,
                successful_bookings=2,
                average_rating=4.5,
                created_at=datetime.utcnow()
            )
        ]
        
        for customer in customers:
            session.add(customer)
        
        await session.commit()
        print("Sample data initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_database())
