import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime
import uuid

from app.models.booking import Booking, BookingHistory
from app.schemas.booking import BookingCreate, BookingUpdate

logger = logging.getLogger(__name__)

class BookingService:
    """Service for booking management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        
        try:
            result = await self.db.execute(
                select(Booking).where(Booking.id == booking_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting booking {booking_id}: {e}")
            return None
    
    async def create_booking(self, booking_data: BookingCreate) -> Booking:
        """Create new booking"""
        
        try:
            booking = Booking(
                id=str(uuid.uuid4()),
                customer_rfc=booking_data.customer_rfc,
                service_id=booking_data.service_id,
                supplier_id=booking_data.supplier_id,
                session_id=booking_data.session_id,
                status="pending",
                priority=booking_data.priority,
                service_parameters=booking_data.service_parameters,
                special_instructions=booking_data.special_instructions,
                estimated_duration_minutes=booking_data.estimated_duration_minutes,
                requested_date=booking_data.requested_date,
                requested_time_slot=booking_data.requested_time_slot,
                service_address=booking_data.service_address,
                service_city=booking_data.service_city,
                service_state=booking_data.service_state,
                service_postal_code=booking_data.service_postal_code,
                latitude=booking_data.latitude,
                longitude=booking_data.longitude,
                quoted_price=booking_data.quoted_price,
                currency=booking_data.currency,
                payment_method=booking_data.payment_method,
                created_at=datetime.utcnow()
            )
            
            self.db.add(booking)
            
            history = BookingHistory(
                booking_id=booking.id,
                new_status="pending",
                changed_by="system",
                change_reason="Booking created",
                created_at=datetime.utcnow()
            )
            
            self.db.add(history)
            await self.db.commit()
            await self.db.refresh(booking)
            
            logger.info(f"Created booking {booking.id}")
            return booking
            
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            await self.db.rollback()
            raise
    
    async def update_booking(
        self, 
        booking_id: str, 
        booking_data: BookingUpdate
    ) -> Optional[Booking]:
        """Update booking information"""
        
        try:
            booking = await self.get_booking(booking_id)
            if not booking:
                return None
            
            update_data = booking_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            await self.db.execute(
                update(Booking)
                .where(Booking.id == booking_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            return await self.get_booking(booking_id)
            
        except Exception as e:
            logger.error(f"Error updating booking {booking_id}: {e}")
            await self.db.rollback()
            raise
    
    async def update_booking_status(
        self,
        booking_id: str,
        new_status: str,
        changed_by: str,
        change_reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Booking]:
        """Update booking status with history tracking"""
        
        try:
            booking = await self.get_booking(booking_id)
            if not booking:
                return None
            
            previous_status = booking.status
            
            update_data = {
                "status": new_status,
                "updated_at": datetime.utcnow()
            }
            
            if new_status == "completed":
                update_data["completed_datetime"] = datetime.utcnow()
            elif new_status == "cancelled":
                update_data["cancelled_at"] = datetime.utcnow()
                if change_reason:
                    update_data["cancellation_reason"] = change_reason
            
            await self.db.execute(
                update(Booking)
                .where(Booking.id == booking_id)
                .values(**update_data)
            )
            
            history = BookingHistory(
                booking_id=booking_id,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=changed_by,
                change_reason=change_reason,
                notes=notes,
                created_at=datetime.utcnow()
            )
            
            self.db.add(history)
            await self.db.commit()
            
            logger.info(f"Updated booking {booking_id} status: {previous_status} -> {new_status}")
            
            return await self.get_booking(booking_id)
            
        except Exception as e:
            logger.error(f"Error updating booking status {booking_id}: {e}")
            await self.db.rollback()
            raise
    
    async def list_bookings(
        self,
        customer_rfc: Optional[str] = None,
        supplier_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Booking]:
        """List bookings with filters"""
        
        try:
            query = select(Booking)
            
            if customer_rfc:
                query = query.where(Booking.customer_rfc == customer_rfc)
            
            if supplier_id:
                query = query.where(Booking.supplier_id == supplier_id)
            
            if status:
                query = query.where(Booking.status == status)
            
            query = query.order_by(Booking.created_at.desc()).limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error listing bookings: {e}")
            return []
    
    async def get_customer_bookings(
        self,
        customer_rfc: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Booking]:
        """Get bookings for a specific customer"""
        
        return await self.list_bookings(
            customer_rfc=customer_rfc,
            status=status,
            limit=limit
        )
    
    async def get_supplier_bookings(
        self,
        supplier_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Booking]:
        """Get bookings for a specific supplier"""
        
        return await self.list_bookings(
            supplier_id=supplier_id,
            status=status,
            limit=limit
        )
    
    async def get_booking_history(self, booking_id: str) -> List[BookingHistory]:
        """Get booking status history"""
        
        try:
            result = await self.db.execute(
                select(BookingHistory)
                .where(BookingHistory.booking_id == booking_id)
                .order_by(BookingHistory.created_at.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting booking history {booking_id}: {e}")
            return []
    
    async def get_active_bookings_count(self, supplier_id: str) -> int:
        """Get count of active bookings for supplier"""
        
        try:
            result = await self.db.execute(
                select(Booking)
                .where(
                    and_(
                        Booking.supplier_id == supplier_id,
                        Booking.status.in_(["pending", "confirmed", "in_progress"])
                    )
                )
            )
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting active bookings count for {supplier_id}: {e}")
            return 0
