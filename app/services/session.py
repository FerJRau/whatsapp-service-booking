import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime, timedelta

from app.models.session import Session, Message
from app.schemas.session import SessionCreate, SessionUpdate, MessageCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

class SessionService:
    """Service for session and message management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(self, session_data: SessionCreate) -> Session:
        """Create new session"""
        
        try:
            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.SESSION_TIMEOUT_MINUTES
            )
            
            session = Session(
                customer_rfc=session_data.customer_rfc,
                phone_number=session_data.phone_number,
                status="active",
                current_step="greeting",
                conversation_context={},
                collected_parameters={},
                service_confidence_score=0,
                service_identification_attempts=0,
                total_messages=0,
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            
            logger.info(f"Created session {session.id} for {session.phone_number}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            await self.db.rollback()
            raise
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        
        try:
            result = await self.db.execute(
                select(Session).where(Session.id == session_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def get_active_session_by_phone(self, phone_number: str) -> Optional[Session]:
        """Get active session for phone number"""
        
        try:
            result = await self.db.execute(
                select(Session).where(
                    and_(
                        Session.phone_number == phone_number,
                        Session.status == "active",
                        Session.expires_at > datetime.utcnow()
                    )
                ).order_by(Session.created_at.desc())
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting active session for {phone_number}: {e}")
            return None
    
    async def update_session(
        self, 
        session_id: str, 
        session_data: Dict[str, Any]
    ) -> Optional[Session]:
        """Update session information"""
        
        try:
            session = await self.get_session(session_id)
            if not session:
                return None
            
            update_data = session_data if isinstance(session_data, dict) else session_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            await self.db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            return await self.get_session(session_id)
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            await self.db.rollback()
            raise
    
    async def add_message(
        self, 
        session_id: str, 
        message_data: Dict[str, Any]
    ) -> Message:
        """Add message to session"""
        
        try:
            message = Message(
                session_id=session_id,
                whatsapp_message_id=message_data.get("whatsapp_message_id"),
                direction=message_data.get("direction", "inbound"),
                message_type=message_data.get("message_type", "text"),
                content=message_data.get("content"),
                media_url=message_data.get("media_url"),
                processed=False,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(message)
            
            await self.db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(
                    total_messages=Session.total_messages + 1,
                    last_message_at=datetime.utcnow(),
                    last_message_content=message_data.get("content")
                )
            )
            
            await self.db.commit()
            await self.db.refresh(message)
            
            logger.info(f"Added {message_data.get('direction', 'unknown')} message to session {session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {e}")
            await self.db.rollback()
            raise
    
    async def get_session_messages(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a session"""
        
        try:
            result = await self.db.execute(
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.timestamp.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting messages for session {session_id}: {e}")
            return []
    
    async def list_sessions(
        self,
        customer_rfc: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Session]:
        """List sessions with filters"""
        
        try:
            query = select(Session)
            
            if customer_rfc:
                query = query.where(Session.customer_rfc == customer_rfc)
            
            if status:
                query = query.where(Session.status == status)
            
            query = query.order_by(Session.created_at.desc()).limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []
    
    async def expire_old_sessions(self) -> int:
        """Expire old sessions"""
        
        try:
            result = await self.db.execute(
                update(Session)
                .where(
                    and_(
                        Session.status == "active",
                        Session.expires_at < datetime.utcnow()
                    )
                )
                .values(status="expired")
            )
            
            await self.db.commit()
            expired_count = result.rowcount
            
            if expired_count > 0:
                logger.info(f"Expired {expired_count} old sessions")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Error expiring sessions: {e}")
            return 0
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session conversation context"""
        
        session = await self.get_session(session_id)
        if not session:
            return {}
        
        messages = await self.get_session_messages(session_id, limit=10)
        
        context = {
            "session_id": session.id,
            "customer_rfc": session.customer_rfc,
            "current_step": session.current_step,
            "identified_service_id": session.identified_service_id,
            "service_confidence_score": session.service_confidence_score,
            "collected_parameters": session.collected_parameters or {},
            "conversation_context": session.conversation_context or {},
            "recent_messages": [
                {
                    "direction": msg.direction,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }
        
        return context
