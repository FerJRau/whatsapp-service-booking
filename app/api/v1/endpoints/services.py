from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.service import (
    Service, ServiceCreate, ServiceUpdate, 
    ServiceIdentificationRequest, ServiceIdentificationResponse
)
from app.services.service import ServiceManager
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/", response_model=List[Service])
async def list_services(
    category: str = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List available services"""
    service_manager = ServiceManager(db)
    services = await service_manager.list_services(category=category, is_active=is_active)
    return services

@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get service by ID"""
    service_manager = ServiceManager(db)
    service = await service_manager.get_service(service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service

@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new service"""
    service_manager = ServiceManager(db)
    
    existing = await service_manager.get_service(service_data.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service already exists"
        )
    
    service = await service_manager.create_service(service_data)
    return service

@router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: str,
    service_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update service information"""
    service_manager = ServiceManager(db)
    
    service = await service_manager.update_service(service_id, service_data)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service

@router.post("/identify", response_model=ServiceIdentificationResponse)
async def identify_service(
    request: ServiceIdentificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Identify service from customer message"""
    ai_service = AIService()
    service_manager = ServiceManager(db)
    
    identification = await ai_service.identify_service(
        message_text=request.message_text,
        customer_rfc=request.customer_rfc,
        conversation_context=request.conversation_context,
        db=db
    )
    
    return identification

@router.get("/category/{category}", response_model=List[Service])
async def get_services_by_category(
    category: str,
    db: AsyncSession = Depends(get_db)
):
    """Get services by category"""
    service_manager = ServiceManager(db)
    services = await service_manager.get_services_by_category(category)
    return services
