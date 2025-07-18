from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.supplier import (
    Supplier, SupplierCreate, SupplierUpdate,
    SupplierMatchRequest, SupplierMatchResponse
)
from app.services.supplier import SupplierService

router = APIRouter()

@router.get("/", response_model=List[Supplier])
async def list_suppliers(
    is_active: bool = True,
    is_verified: bool = None,
    service_id: str = None,
    city: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List suppliers with optional filters"""
    service = SupplierService(db)
    suppliers = await service.list_suppliers(
        is_active=is_active,
        is_verified=is_verified,
        service_id=service_id,
        city=city
    )
    return suppliers

@router.get("/{supplier_id}", response_model=Supplier)
async def get_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get supplier by ID"""
    service = SupplierService(db)
    supplier = await service.get_supplier(supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return supplier

@router.post("/", response_model=Supplier, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new supplier"""
    service = SupplierService(db)
    
    existing = await service.get_supplier(supplier_data.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Supplier already exists"
        )
    
    supplier = await service.create_supplier(supplier_data)
    return supplier

@router.put("/{supplier_id}", response_model=Supplier)
async def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update supplier information"""
    service = SupplierService(db)
    
    supplier = await service.update_supplier(supplier_id, supplier_data)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return supplier

@router.post("/match", response_model=SupplierMatchResponse)
async def match_suppliers(
    match_request: SupplierMatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Match suppliers for a service request"""
    service = SupplierService(db)
    
    match_result = await service.match_suppliers(match_request)
    return match_result

@router.get("/{supplier_id}/availability")
async def check_supplier_availability(
    supplier_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Check supplier availability"""
    service = SupplierService(db)
    supplier = await service.get_supplier(supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    availability = await service.check_availability(supplier_id)
    return {
        "supplier_id": supplier_id,
        "is_available": availability,
        "current_jobs": supplier.current_active_jobs,
        "max_jobs": supplier.max_concurrent_jobs
    }
