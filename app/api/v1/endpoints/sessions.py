from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.session import Session, SessionCreate, SessionUpdate, Message, MessageCreate
from app.services.session import SessionService

router = APIRouter()

@router.get("/", response_model=List[Session])
async def list_sessions(
    customer_rfc: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List sessions with optional filters"""
    service = SessionService(db)
    sessions = await service.list_sessions(
        customer_rfc=customer_rfc,
        status=status,
        limit=limit,
        offset=offset
    )
    return sessions

@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session by ID"""
    service = SessionService(db)
    session = await service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session

@router.post("/", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new session"""
    service = SessionService(db)
    session = await service.create_session(session_data)
    return session

@router.put("/{session_id}", response_model=Session)
async def update_session(
    session_id: str,
    session_data: SessionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update session information"""
    service = SessionService(db)
    
    session = await service.update_session(session_id, session_data)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session

@router.get("/phone/{phone_number}/active", response_model=Session)
async def get_active_session(
    phone_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get active session for phone number"""
    service = SessionService(db)
    session = await service.get_active_session_by_phone(phone_number)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )
    
    return session

@router.get("/{session_id}/messages", response_model=List[Message])
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a session"""
    service = SessionService(db)
    messages = await service.get_session_messages(
        session_id=session_id,
        limit=limit,
        offset=offset
    )
    return messages

@router.post("/{session_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def add_session_message(
    session_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add message to session"""
    service = SessionService(db)
    
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    message = await service.add_message(session_id, message_data)
    return message
