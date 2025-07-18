import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from datetime import datetime
import math

from app.models.supplier import Supplier, SupplierPerformance
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierMatchRequest, SupplierMatchResponse

logger = logging.getLogger(__name__)

class SupplierService:
    """Service for supplier management and matching"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Get supplier by ID"""
        
        try:
            result = await self.db.execute(
                select(Supplier).where(Supplier.id == supplier_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier {supplier_id}: {e}")
            return None
    
    async def list_suppliers(
        self,
        is_active: bool = True,
        is_verified: Optional[bool] = None,
        service_id: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Supplier]:
        """List suppliers with filters"""
        
        try:
            query = select(Supplier)
            
            if is_active is not None:
                query = query.where(Supplier.is_active == is_active)
            
            if is_verified is not None:
                query = query.where(Supplier.is_verified == is_verified)
            
            if service_id:
                query = query.where(Supplier.services_offered.contains([service_id]))
            
            if city:
                query = query.where(Supplier.city.ilike(f"%{city}%"))
            
            query = query.order_by(Supplier.average_rating.desc())
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error listing suppliers: {e}")
            return []
    
    async def create_supplier(self, supplier_data: SupplierCreate) -> Supplier:
        """Create new supplier"""
        
        try:
            supplier = Supplier(
                id=supplier_data.id,
                business_name=supplier_data.business_name,
                contact_name=supplier_data.contact_name,
                phone_number=supplier_data.phone_number,
                email=supplier_data.email,
                whatsapp_number=supplier_data.whatsapp_number,
                business_type=supplier_data.business_type,
                registration_number=supplier_data.registration_number,
                tax_id=supplier_data.tax_id,
                street_address=supplier_data.street_address,
                city=supplier_data.city,
                state=supplier_data.state,
                postal_code=supplier_data.postal_code,
                country=supplier_data.country,
                service_radius_km=supplier_data.service_radius_km,
                service_areas=supplier_data.service_areas,
                services_offered=supplier_data.services_offered,
                specializations=supplier_data.specializations,
                certifications=supplier_data.certifications,
                is_active=supplier_data.is_active,
                is_verified=supplier_data.is_verified,
                is_premium_partner=supplier_data.is_premium_partner,
                operating_hours=supplier_data.operating_hours,
                max_concurrent_jobs=supplier_data.max_concurrent_jobs,
                base_rate=supplier_data.base_rate,
                rate_currency=supplier_data.rate_currency,
                payment_terms=supplier_data.payment_terms,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            
            self.db.add(supplier)
            await self.db.commit()
            await self.db.refresh(supplier)
            
            logger.info(f"Created supplier {supplier.id}")
            return supplier
            
        except Exception as e:
            logger.error(f"Error creating supplier: {e}")
            await self.db.rollback()
            raise
    
    async def update_supplier(
        self, 
        supplier_id: str, 
        supplier_data: SupplierUpdate
    ) -> Optional[Supplier]:
        """Update supplier information"""
        
        try:
            supplier = await self.get_supplier(supplier_id)
            if not supplier:
                return None
            
            update_data = supplier_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            await self.db.execute(
                update(Supplier)
                .where(Supplier.id == supplier_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            return await self.get_supplier(supplier_id)
            
        except Exception as e:
            logger.error(f"Error updating supplier {supplier_id}: {e}")
            await self.db.rollback()
            raise
    
    async def match_suppliers(self, match_request: SupplierMatchRequest) -> SupplierMatchResponse:
        """Match suppliers for a service request"""
        
        try:
            query = select(Supplier).where(
                and_(
                    Supplier.is_active == True,
                    Supplier.is_verified == True,
                    Supplier.services_offered.contains([match_request.service_id]),
                    Supplier.current_active_jobs < Supplier.max_concurrent_jobs
                )
            )
            
            if match_request.customer_location:
                pass
            
            if match_request.priority == "emergency":
                query = query.where(Supplier.is_premium_partner == True)
            
            query = query.order_by(
                Supplier.is_premium_partner.desc(),
                Supplier.average_rating.desc(),
                Supplier.completion_rate.desc(),
                Supplier.average_response_time_minutes.asc()
            ).limit(match_request.max_suppliers)
            
            result = await self.db.execute(query)
            matched_suppliers = result.scalars().all()
            
            total_query = select(Supplier).where(
                and_(
                    Supplier.is_active == True,
                    Supplier.is_verified == True,
                    Supplier.services_offered.contains([match_request.service_id])
                )
            )
            total_result = await self.db.execute(total_query)
            total_available = len(total_result.scalars().all())
            
            match_criteria = {
                "service_id": match_request.service_id,
                "priority": match_request.priority,
                "geographic_filter": bool(match_request.customer_location),
                "max_suppliers": match_request.max_suppliers
            }
            
            return SupplierMatchResponse(
                matched_suppliers=matched_suppliers,
                match_criteria=match_criteria,
                total_available=total_available
            )
            
        except Exception as e:
            logger.error(f"Error matching suppliers: {e}")
            return SupplierMatchResponse(
                matched_suppliers=[],
                match_criteria={},
                total_available=0
            )
    
    async def check_availability(self, supplier_id: str) -> bool:
        """Check if supplier is currently available"""
        
        supplier = await self.get_supplier(supplier_id)
        if not supplier:
            return False
        
        return supplier.is_available
    
    async def update_supplier_stats(
        self,
        supplier_id: str,
        job_assigned: bool = False,
        job_completed: bool = False,
        response_time_minutes: Optional[float] = None,
        customer_rating: Optional[float] = None
    ) -> None:
        """Update supplier performance statistics"""
        
        try:
            supplier = await self.get_supplier(supplier_id)
            if not supplier:
                return
            
            updates = {}
            
            if job_assigned:
                updates["total_jobs_assigned"] = supplier.total_jobs_assigned + 1
                updates["current_active_jobs"] = supplier.current_active_jobs + 1
            
            if job_completed:
                updates["total_jobs_completed"] = supplier.total_jobs_completed + 1
                updates["current_active_jobs"] = max(0, supplier.current_active_jobs - 1)
                
                total_assigned = supplier.total_jobs_assigned
                total_completed = supplier.total_jobs_completed + 1
                updates["completion_rate"] = (total_completed / total_assigned) * 100 if total_assigned > 0 else 0
            
            if response_time_minutes is not None:
                if supplier.average_response_time_minutes == 0:
                    updates["average_response_time_minutes"] = response_time_minutes
                else:
                    total_jobs = supplier.total_jobs_assigned
                    current_total = supplier.average_response_time_minutes * total_jobs
                    new_average = (current_total + response_time_minutes) / (total_jobs + 1)
                    updates["average_response_time_minutes"] = round(new_average, 2)
            
            if customer_rating is not None:
                if supplier.average_rating == 0:
                    updates["average_rating"] = customer_rating
                else:
                    total_jobs = supplier.total_jobs_completed
                    current_total = supplier.average_rating * total_jobs
                    new_average = (current_total + customer_rating) / (total_jobs + 1)
                    updates["average_rating"] = round(new_average, 2)
            
            if updates:
                updates["last_active"] = datetime.utcnow()
                
                await self.db.execute(
                    update(Supplier)
                    .where(Supplier.id == supplier_id)
                    .values(**updates)
                )
                await self.db.commit()
                
        except Exception as e:
            logger.error(f"Error updating supplier stats {supplier_id}: {e}")
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula"""
        
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
