import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.services.ai_service import AIService
from app.services.session import SessionService
from app.core.config import settings

logger = logging.getLogger(__name__)

class EscalationService:
    """Service for managing escalation to human agents"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
        self.session_service = SessionService(db)
    
    async def should_escalate(
        self, 
        session: Any, 
        reason: str,
        message_content: Optional[str] = None
    ) -> bool:
        """Determine if session should be escalated to human agent"""
        
        try:
            escalation_triggers = {
                "low_service_confidence": session.service_confidence_score < 50,
                "multiple_identification_attempts": session.service_identification_attempts >= 3,
                "no_suppliers_available": reason == "no_suppliers_available",
                "customer_frustration": False,  # Will be determined by sentiment analysis
                "complex_request": False,  # Will be determined by AI analysis
                "emergency_service": False,  # Will be determined by service type
                "system_error": reason == "system_error"
            }
            
            if message_content:
                sentiment = await self.ai_service.analyze_sentiment(message_content)
                escalation_triggers["customer_frustration"] = (
                    sentiment.get("frustration_level", 0) > 70 or
                    sentiment.get("escalation_recommended", False)
                )
            
            if session.identified_service_id:
                escalation_triggers["emergency_service"] = False
            
            escalation_triggers["complex_request"] = session.total_messages > 10
            
            should_escalate = any(escalation_triggers.values())
            
            logger.info(f"Escalation check for session {session.id}: {escalation_triggers}")
            return should_escalate
            
        except Exception as e:
            logger.error(f"Error checking escalation for session {session.id}: {e}")
            return True  # Escalate on error to be safe
    
    async def escalate_session(
        self, 
        session_id: str, 
        reason: str,
        agent_id: Optional[str] = None
    ) -> bool:
        """Escalate session to human agent"""
        
        try:
            await self.session_service.update_session(session_id, {
                "status": "escalated",
                "escalation_reason": reason,
                "escalated_at": datetime.utcnow(),
                "escalated_to": agent_id or "general_queue"
            })
            
            
            logger.info(f"Escalated session {session_id} to human agent. Reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating session {session_id}: {e}")
            return False
    
    async def prepare_escalation_context(self, session_id: str) -> Dict[str, Any]:
        """Prepare context information for human agent"""
        
        try:
            context = await self.session_service.get_session_context(session_id)
            
            escalation_context = {
                **context,
                "escalation_summary": await self._generate_escalation_summary(context),
                "recommended_actions": await self._generate_recommended_actions(context),
                "customer_sentiment": "neutral",  # Would be calculated from recent messages
                "urgency_level": "medium",  # Would be determined by various factors
                "estimated_resolution_time": "15 minutes"  # Based on complexity
            }
            
            return escalation_context
            
        except Exception as e:
            logger.error(f"Error preparing escalation context for {session_id}: {e}")
            return {}
    
    async def _generate_escalation_summary(self, context: Dict[str, Any]) -> str:
        """Generate summary for human agent"""
        
        try:
            prompt = f"""
            Genera un resumen conciso para un agente humano sobre esta sesión escalada:
            
            Contexto: {context}
            
            Incluye:
            - Qué servicio busca el cliente
            - Problemas encontrados
            - Información ya recopilada
            - Próximos pasos recomendados
            
            Máximo 200 palabras.
            """
            
            return f"Cliente busca servicio. Escalado por: {context.get('escalation_reason', 'unknown')}. Requiere atención humana."
            
        except Exception as e:
            logger.error(f"Error generating escalation summary: {e}")
            return "Sesión escalada - requiere revisión manual."
    
    async def _generate_recommended_actions(self, context: Dict[str, Any]) -> List[str]:
        """Generate recommended actions for human agent"""
        
        try:
            actions = []
            
            escalation_reason = context.get("escalation_reason", "")
            
            if "low_service_confidence" in escalation_reason:
                actions.append("Clarificar qué servicio específico necesita el cliente")
            
            if "no_suppliers_available" in escalation_reason:
                actions.append("Buscar proveedores alternativos o programar para más tarde")
            
            if "customer_frustration" in escalation_reason:
                actions.append("Disculparse y ofrecer compensación si es apropiado")
            
            if not actions:
                actions.append("Revisar conversación completa y continuar asistencia")
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating recommended actions: {e}")
            return ["Revisar sesión y proporcionar asistencia personalizada"]
    
    async def handle_agent_takeover(
        self, 
        session_id: str, 
        agent_id: str
    ) -> bool:
        """Handle when human agent takes over session"""
        
        try:
            await self.session_service.update_session(session_id, {
                "escalated_to": agent_id,
                "current_step": "human_agent"
            })
            
            
            logger.info(f"Agent {agent_id} took over session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling agent takeover for {session_id}: {e}")
            return False
    
    async def resolve_escalation(
        self, 
        session_id: str, 
        resolution_notes: str
    ) -> bool:
        """Mark escalation as resolved"""
        
        try:
            await self.session_service.update_session(session_id, {
                "status": "completed",
                "current_step": "resolved"
            })
            
            
            logger.info(f"Resolved escalation for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving escalation for {session_id}: {e}")
            return False
