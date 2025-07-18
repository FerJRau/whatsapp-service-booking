import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerProfile

logger = logging.getLogger(__name__)

class CustomerService:
    """Service for customer management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_customer_by_rfc(self, rfc: str) -> Optional[Customer]:
        """Get customer by RFC"""
        
        try:
            result = await self.db.execute(
                select(Customer).where(Customer.rfc == rfc)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting customer by RFC {rfc}: {e}")
            return None
    
    async def get_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        """Get customer by phone number"""
        
        try:
            result = await self.db.execute(
                select(Customer).where(Customer.phone_number == phone_number)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting customer by phone {phone_number}: {e}")
            return None
    
    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create new customer"""
        
        try:
            customer = Customer(
                rfc=customer_data.rfc,
                phone_number=customer_data.phone_number,
                first_name=customer_data.first_name,
                last_name=customer_data.last_name,
                email=customer_data.email,
                street_address=customer_data.street_address,
                city=customer_data.city,
                state=customer_data.state,
                postal_code=customer_data.postal_code,
                country=customer_data.country,
                tier=customer_data.tier,
                preferred_language=customer_data.preferred_language,
                communication_preferences=customer_data.communication_preferences,
                service_preferences=customer_data.service_preferences,
                created_at=datetime.utcnow(),
                last_interaction=datetime.utcnow()
            )
            
            self.db.add(customer)
            await self.db.commit()
            await self.db.refresh(customer)
            
            logger.info(f"Created customer {customer.rfc}")
            return customer
            
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            await self.db.rollback()
            raise
    
    async def update_customer(
        self, 
        rfc: str, 
        customer_data: CustomerUpdate
    ) -> Optional[Customer]:
        """Update customer information"""
        
        try:
            customer = await self.get_customer_by_rfc(rfc)
            if not customer:
                return None
            
            update_data = customer_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            update_data["last_interaction"] = datetime.utcnow()
            
            await self.db.execute(
                update(Customer)
                .where(Customer.rfc == rfc)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            return await self.get_customer_by_rfc(rfc)
            
        except Exception as e:
            logger.error(f"Error updating customer {rfc}: {e}")
            await self.db.rollback()
            raise
    
    async def get_customer_profile(self, rfc: str) -> Optional[CustomerProfile]:
        """Get customer profile summary"""
        
        customer = await self.get_customer_by_rfc(rfc)
        if not customer:
            return None
        
        return CustomerProfile(
            rfc=customer.rfc,
            full_name=customer.full_name,
            phone_number=customer.phone_number,
            email=customer.email,
            tier=customer.tier,
            success_rate=customer.success_rate,
            total_bookings=customer.total_bookings,
            average_rating=customer.average_rating,
            last_interaction=customer.last_interaction,
            is_verified=customer.is_verified
        )
    
    async def update_customer_interaction(self, rfc: str) -> None:
        """Update customer last interaction timestamp"""
        
        try:
            await self.db.execute(
                update(Customer)
                .where(Customer.rfc == rfc)
                .values(last_interaction=datetime.utcnow())
            )
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error updating customer interaction {rfc}: {e}")
    
    async def update_customer_stats(
        self, 
        rfc: str, 
        booking_completed: bool = False,
        rating: Optional[float] = None,
        amount_spent: Optional[float] = None
    ) -> None:
        """Update customer statistics"""
        
        try:
            customer = await self.get_customer_by_rfc(rfc)
            if not customer:
                return
            
            updates = {}
            
            if booking_completed:
                updates["total_bookings"] = customer.total_bookings + 1
                updates["successful_bookings"] = customer.successful_bookings + 1
            
            if rating is not None:
                if customer.average_rating == 0:
                    updates["average_rating"] = rating
                else:
                    total_ratings = customer.total_bookings
                    current_total = customer.average_rating * total_ratings
                    new_average = (current_total + rating) / (total_ratings + 1)
                    updates["average_rating"] = round(new_average, 2)
            
            if amount_spent is not None:
                updates["total_spent"] = customer.total_spent + amount_spent
            
            if updates:
                await self.db.execute(
                    update(Customer)
                    .where(Customer.rfc == rfc)
                    .values(**updates)
                )
                await self.db.commit()
                
        except Exception as e:
            logger.error(f"Error updating customer stats {rfc}: {e}")
    
    async def list_customers(
        self,
        tier: Optional[str] = None,
        is_active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Customer]:
        """List customers with filters"""
        
        try:
            query = select(Customer)
            
            if tier:
                query = query.where(Customer.tier == tier)
            
            if is_active is not None:
                query = query.where(Customer.is_active == is_active)
            
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error listing customers: {e}")
            return []
