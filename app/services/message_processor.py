import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.session import SessionService
from app.services.customer import CustomerService
from app.services.ai_service import AIService
from app.services.whatsapp import WhatsAppService
from app.services.escalation import EscalationService
from app.core.config import settings

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Core message processing engine"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_service = SessionService(db)
        self.customer_service = CustomerService(db)
        self.ai_service = AIService()
        self.whatsapp_service = WhatsAppService()
        self.escalation_service = EscalationService(db)
    
    async def process_message(
        self,
        phone_number: str,
        message_data: Dict[str, Any],
        webhook_value: Dict[str, Any]
    ) -> None:
        """Main message processing pipeline"""
        
        try:
            start_time = datetime.utcnow()
            
            message_content = await self._extract_message_content(message_data)
            message_type = message_data.get("type", "text")
            message_id = message_data.get("id")
            
            logger.info(f"Processing {message_type} message from {phone_number}")
            
            session = await self._get_or_create_session(phone_number, message_content)
            
            await self.session_service.add_message(session.id, {
                "session_id": session.id,
                "whatsapp_message_id": message_id,
                "direction": "inbound",
                "message_type": message_type,
                "content": message_content
            })
            
            await self._process_message_by_state(session, message_content, message_data)
            
            if message_id:
                await self.whatsapp_service.mark_message_read(message_id)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"Message processed in {processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await self._handle_processing_error(phone_number, str(e))
    
    async def _extract_message_content(self, message_data: Dict[str, Any]) -> str:
        """Extract text content from message"""
        
        message_type = message_data.get("type")
        
        if message_type == "text":
            return message_data.get("text", {}).get("body", "")
        elif message_type == "interactive":
            interactive = message_data.get("interactive", {})
            if "button_reply" in interactive:
                return interactive["button_reply"].get("title", "")
            elif "list_reply" in interactive:
                return interactive["list_reply"].get("title", "")
        elif message_type in ["image", "document", "audio", "video"]:
            return f"[{message_type.upper()}] Media file received"
        elif message_type == "location":
            location = message_data.get("location", {})
            return f"Location: {location.get('latitude')}, {location.get('longitude')}"
        
        return ""
    
    async def _get_or_create_session(
        self, 
        phone_number: str, 
        message_content: str
    ) -> Any:
        """Get existing active session or create new one"""
        
        session = await self.session_service.get_active_session_by_phone(phone_number)
        
        if session and not session.is_expired:
            await self.session_service.update_session(session.id, {
                "last_message_at": datetime.utcnow(),
                "last_message_content": message_content,
                "total_messages": session.total_messages + 1
            })
            return session
        
        customer = await self.customer_service.get_customer_by_phone(phone_number)
        customer_rfc = customer.rfc if customer else None
        
        session = await self.session_service.create_session({
            "customer_rfc": customer_rfc or "UNKNOWN",
            "phone_number": phone_number
        })
        
        logger.info(f"Created new session {session.id} for {phone_number}")
        return session
    
    async def _process_message_by_state(
        self,
        session: Any,
        message_content: str,
        message_data: Dict[str, Any]
    ) -> None:
        """Process message based on current session state"""
        
        current_step = session.current_step or "greeting"
        
        if current_step == "greeting":
            await self._handle_greeting(session, message_content)
        elif current_step == "customer_validation":
            await self._handle_customer_validation(session, message_content)
        elif current_step == "service_identification":
            await self._handle_service_identification(session, message_content)
        elif current_step == "parameter_collection":
            await self._handle_parameter_collection(session, message_content)
        elif current_step == "supplier_matching":
            await self._handle_supplier_matching(session, message_content)
        elif current_step == "booking_confirmation":
            await self._handle_booking_confirmation(session, message_content)
        else:
            await self._handle_unknown_state(session, message_content)
    
    async def _handle_greeting(self, session: Any, message_content: str) -> None:
        """Handle initial greeting and customer identification"""
        
        customer = await self.customer_service.get_customer_by_phone(session.phone_number)
        
        if customer:
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text=f"¡Hola {customer.first_name or 'estimado cliente'}! ¿En qué puedo ayudarte hoy?"
            )
            
            await self.session_service.update_session(session.id, {
                "current_step": "service_identification",
                "customer_rfc": customer.rfc
            })
        else:
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text="¡Bienvenido! Para brindarte el mejor servicio, necesito tu RFC. Por favor compártelo conmigo."
            )
            
            await self.session_service.update_session(session.id, {
                "current_step": "customer_validation"
            })
    
    async def _handle_customer_validation(self, session: Any, message_content: str) -> None:
        """Handle customer RFC validation and registration"""
        
        rfc = await self.ai_service.extract_rfc(message_content)
        
        if not rfc:
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text="No pude identificar un RFC válido. Por favor envía tu RFC en el formato correcto (ej: ABCD123456EF1)."
            )
            return
        
        customer = await self.customer_service.get_customer_by_rfc(rfc)
        
        if customer:
            if customer.phone_number != session.phone_number:
                await self.customer_service.update_customer(rfc, {
                    "phone_number": session.phone_number
                })
        else:
            customer = await self.customer_service.create_customer({
                "rfc": rfc,
                "phone_number": session.phone_number
            })
        
        await self.whatsapp_service.send_text_message(
            to=session.phone_number,
            text=f"Perfecto, {customer.first_name or 'estimado cliente'}. ¿En qué servicio puedo ayudarte?"
        )
        
        await self.session_service.update_session(session.id, {
            "current_step": "service_identification",
            "customer_rfc": rfc
        })
    
    async def _handle_service_identification(self, session: Any, message_content: str) -> None:
        """Handle AI-powered service identification"""
        
        identification = await self.ai_service.identify_service(
            message_text=message_content,
            customer_rfc=session.customer_rfc,
            conversation_context=session.conversation_context,
            db=self.db
        )
        
        if identification.confidence_score >= 80:
            await self.session_service.update_session(session.id, {
                "identified_service_id": identification.identified_service.id,
                "service_confidence_score": identification.confidence_score,
                "current_step": "parameter_collection"
            })
            
            if identification.missing_parameters:
                questions = identification.clarification_questions
                await self.whatsapp_service.send_text_message(
                    to=session.phone_number,
                    text=f"Entiendo que necesitas {identification.identified_service.name}. " +
                          f"Para continuar, necesito algunos detalles: {', '.join(questions)}"
                )
            else:
                await self.session_service.update_session(session.id, {
                    "current_step": "supplier_matching"
                })
                await self._handle_supplier_matching(session, "")
        
        elif identification.confidence_score >= 50:
            alternatives = [s.name for s in identification.alternative_services[:3]]
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text=f"Creo que necesitas {identification.identified_service.name}, " +
                      f"pero también podrías estar buscando: {', '.join(alternatives)}. " +
                      "¿Puedes ser más específico?"
            )
        else:
            await self._check_escalation_needed(session, "low_service_confidence")
    
    async def _handle_parameter_collection(self, session: Any, message_content: str) -> None:
        """Handle collection of service parameters"""
        
        extracted_params = await self.ai_service.extract_service_parameters(
            message_text=message_content,
            service_id=session.identified_service_id,
            existing_parameters=session.collected_parameters or {}
        )
        
        current_params = session.collected_parameters or {}
        current_params.update(extracted_params)
        
        await self.session_service.update_session(session.id, {
            "collected_parameters": current_params
        })
        
        service = await self.ai_service.get_service(session.identified_service_id)
        missing_params = []
        
        for param in service.required_parameters or []:
            if param not in current_params:
                missing_params.append(param)
        
        if missing_params:
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text=f"Necesito algunos detalles adicionales: {', '.join(missing_params)}"
            )
        else:
            await self.session_service.update_session(session.id, {
                "current_step": "supplier_matching"
            })
            await self._handle_supplier_matching(session, "")
    
    async def _handle_supplier_matching(self, session: Any, message_content: str) -> None:
        """Handle supplier matching and communication"""
        
        from app.services.supplier import SupplierService
        
        supplier_service = SupplierService(self.db)
        
        match_request = {
            "service_id": session.identified_service_id,
            "customer_location": session.collected_parameters.get("location"),
            "service_parameters": session.collected_parameters,
            "priority": "normal",
            "max_suppliers": 3
        }
        
        match_result = await supplier_service.match_suppliers(match_request)
        
        if match_result.matched_suppliers:
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text="Perfecto. Estoy contactando a los mejores proveedores para tu solicitud. Te responderé en breve."
            )
            
            await self.session_service.update_session(session.id, {
                "current_step": "booking_confirmation"
            })
            
            import asyncio
            await asyncio.sleep(2)
            
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text=f"¡Excelente! {match_result.matched_suppliers[0].business_name} puede atenderte. " +
                      "¿Confirmas tu solicitud de servicio?"
            )
        else:
            await self._check_escalation_needed(session, "no_suppliers_available")
    
    async def _handle_booking_confirmation(self, session: Any, message_content: str) -> None:
        """Handle booking confirmation"""
        
        confirmation = await self.ai_service.detect_confirmation(message_content)
        
        if confirmation:
            from app.services.booking import BookingService
            
            booking_service = BookingService(self.db)
            
            booking_data = {
                "customer_rfc": session.customer_rfc,
                "service_id": session.identified_service_id,
                "session_id": session.id,
                "service_parameters": session.collected_parameters,
                "priority": "normal"
            }
            
            booking = await booking_service.create_booking(booking_data)
            
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text=f"¡Perfecto! Tu solicitud ha sido confirmada. Número de referencia: {booking.id[:8]}. " +
                      "Te mantendremos informado sobre el progreso."
            )
            
            await self.session_service.update_session(session.id, {
                "status": "completed",
                "current_step": "completed"
            })
        else:
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text="Entiendo. ¿Hay algo que te gustaría modificar en tu solicitud?"
            )
    
    async def _handle_unknown_state(self, session: Any, message_content: str) -> None:
        """Handle unknown or error states"""
        
        await self.whatsapp_service.send_text_message(
            to=session.phone_number,
            text="Disculpa, parece que hubo un problema. ¿Puedes repetir tu solicitud?"
        )
        
        await self.session_service.update_session(session.id, {
            "current_step": "service_identification"
        })
    
    async def _check_escalation_needed(self, session: Any, reason: str) -> None:
        """Check if escalation to human agent is needed"""
        
        escalation_needed = await self.escalation_service.should_escalate(
            session=session,
            reason=reason
        )
        
        if escalation_needed:
            await self.escalation_service.escalate_session(session.id, reason)
            
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text="Te estoy conectando con uno de nuestros especialistas que podrá ayudarte mejor. " +
                      "En un momento se pondrá en contacto contigo."
            )
        else:
            await self.whatsapp_service.send_text_message(
                to=session.phone_number,
                text="Disculpa, no pude procesar tu solicitud. ¿Puedes intentar de nuevo con más detalles?"
            )
    
    async def _handle_processing_error(self, phone_number: str, error: str) -> None:
        """Handle processing errors"""
        
        logger.error(f"Processing error for {phone_number}: {error}")
        
        try:
            await self.whatsapp_service.send_text_message(
                to=phone_number,
                text="Disculpa, hubo un problema técnico. Por favor intenta de nuevo en unos momentos."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
