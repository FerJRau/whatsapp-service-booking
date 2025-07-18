from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.booking import Booking, BookingCreate, BookingUpdate, BookingStatusUpdate
from app.services.booking import BookingService

router = APIRouter()

@router.get("/", response_model=List[Booking])
async def list_bookings(
    customer_rfc: Optional[str] = None,
    supplier_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List bookings with optional filters"""
    service = BookingService(db)
    bookings = await service.list_bookings(
        customer_rfc=customer_rfc,
        supplier_id=supplier_id,
        status=status,
        limit=limit,
        offset=offset
    )
    return bookings

@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get booking by ID"""
    service = BookingService(db)
    booking = await service.get_booking(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking

@router.post("/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new booking"""
    service = BookingService(db)
    booking = await service.create_booking(booking_data)
    return booking

@router.put("/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update booking information"""
    service = BookingService(db)
    
    booking = await service.update_booking(booking_id, booking_data)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking

@router.post("/{booking_id}/status", response_model=Booking)
async def update_booking_status(
    booking_id: str,
    status_update: BookingStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update booking status with history tracking"""
    service = BookingService(db)
    
    booking = await service.update_booking_status(
        booking_id=booking_id,
        new_status=status_update.new_status,
        changed_by=status_update.changed_by,
        change_reason=status_update.change_reason,
        notes=status_update.notes
    )
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking

@router.get("/customer/{customer_rfc}", response_model=List[Booking])
async def get_customer_bookings(
    customer_rfc: str,
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get bookings for a specific customer"""
    service = BookingService(db)
    bookings = await service.get_customer_bookings(
        customer_rfc=customer_rfc,
        status=status,
        limit=limit
    )
    return bookings

@router.get("/supplier/{supplier_id}", response_model=List[Booking])
async def get_supplier_bookings(
    supplier_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get bookings for a specific supplier"""
    service = BookingService(db)
    bookings = await service.get_supplier_bookings(
        supplier_id=supplier_id,
        status=status,
        limit=limit
    )
    return bookings
