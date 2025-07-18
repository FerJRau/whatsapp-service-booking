from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate, CustomerProfile
from app.services.customer import CustomerService

router = APIRouter()

@router.get("/{rfc}", response_model=Customer)
async def get_customer(
    rfc: str,
    db: AsyncSession = Depends(get_db)
):
    """Get customer by RFC"""
    service = CustomerService(db)
    customer = await service.get_customer_by_rfc(rfc)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer

@router.get("/{rfc}/profile", response_model=CustomerProfile)
async def get_customer_profile(
    rfc: str,
    db: AsyncSession = Depends(get_db)
):
    """Get customer profile summary"""
    service = CustomerService(db)
    profile = await service.get_customer_profile(rfc)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return profile

@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new customer"""
    service = CustomerService(db)
    
    existing = await service.get_customer_by_rfc(customer_data.rfc)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer already exists"
        )
    
    customer = await service.create_customer(customer_data)
    return customer

@router.put("/{rfc}", response_model=Customer)
async def update_customer(
    rfc: str,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update customer information"""
    service = CustomerService(db)
    
    customer = await service.update_customer(rfc, customer_data)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer

@router.get("/phone/{phone_number}", response_model=Customer)
async def get_customer_by_phone(
    phone_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get customer by phone number"""
    service = CustomerService(db)
    customer = await service.get_customer_by_phone(phone_number)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer
