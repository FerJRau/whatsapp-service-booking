import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.models.service import Service, ServiceParameter
from app.schemas.service import ServiceCreate, ServiceUpdate

logger = logging.getLogger(__name__)

class ServiceManager:
    """Service for managing services and service parameters"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_service(self, service_id: str) -> Optional[Service]:
        """Get service by ID"""
        
        try:
            result = await self.db.execute(
                select(Service).where(Service.id == service_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting service {service_id}: {e}")
            return None
    
    async def list_services(
        self,
        category: Optional[str] = None,
        is_active: bool = True
    ) -> List[Service]:
        """List services with optional filters"""
        
        try:
            query = select(Service)
            
            if category:
                query = query.where(Service.category == category)
            
            if is_active is not None:
                query = query.where(Service.is_active == is_active)
            
            query = query.order_by(Service.name)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error listing services: {e}")
            return []
    
    async def create_service(self, service_data: ServiceCreate) -> Service:
        """Create new service"""
        
        try:
            service = Service(
                id=service_data.id,
                name=service_data.name,
                description=service_data.description,
                category=service_data.category,
                subcategory=service_data.subcategory,
                complexity_level=service_data.complexity_level,
                estimated_duration_minutes=service_data.estimated_duration_minutes,
                base_price=service_data.base_price,
                price_currency=service_data.price_currency,
                required_parameters=service_data.required_parameters,
                optional_parameters=service_data.optional_parameters,
                service_keywords=service_data.service_keywords,
                is_active=service_data.is_active,
                is_emergency_service=service_data.is_emergency_service,
                requires_appointment=service_data.requires_appointment,
                available_hours=service_data.available_hours,
                geographic_restrictions=service_data.geographic_restrictions
            )
            
            self.db.add(service)
            await self.db.commit()
            await self.db.refresh(service)
            
            logger.info(f"Created service {service.id}")
            return service
            
        except Exception as e:
            logger.error(f"Error creating service: {e}")
            await self.db.rollback()
            raise
    
    async def update_service(
        self, 
        service_id: str, 
        service_data: ServiceUpdate
    ) -> Optional[Service]:
        """Update service information"""
        
        try:
            service = await self.get_service(service_id)
            if not service:
                return None
            
            update_data = service_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            await self.db.execute(
                update(Service)
                .where(Service.id == service_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            return await self.get_service(service_id)
            
        except Exception as e:
            logger.error(f"Error updating service {service_id}: {e}")
            await self.db.rollback()
            raise
    
    async def get_services_by_category(self, category: str) -> List[Service]:
        """Get services by category"""
        
        try:
            result = await self.db.execute(
                select(Service)
                .where(Service.category == category)
                .where(Service.is_active == True)
                .order_by(Service.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting services by category {category}: {e}")
            return []
    
    async def search_services(self, query: str) -> List[Service]:
        """Search services by name, description, or keywords"""
        
        try:
            result = await self.db.execute(
                select(Service)
                .where(
                    Service.is_active == True
                ).where(
                    Service.name.ilike(f"%{query}%") |
                    Service.description.ilike(f"%{query}%")
                )
                .order_by(Service.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching services: {e}")
            return []
