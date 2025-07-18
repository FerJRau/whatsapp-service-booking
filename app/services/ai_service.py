import openai
import logging
import json
import re
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.service import ServiceIdentificationResponse, Service

logger = logging.getLogger(__name__)

class AIService:
    """Service for OpenAI integration and AI-powered features"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    async def identify_service(
        self,
        message_text: str,
        customer_rfc: Optional[str] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> ServiceIdentificationResponse:
        """Identify service from customer message using AI"""
        
        try:
            from app.services.service import ServiceManager
            service_manager = ServiceManager(db)
            available_services = await service_manager.list_services(is_active=True)
            
            services_context = []
            for service in available_services:
                services_context.append({
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "category": service.category,
                    "keywords": service.service_keywords or []
                })
            
            prompt = f"""
            Analiza el siguiente mensaje de un cliente y identifica qué servicio necesita.
            
            Mensaje del cliente: "{message_text}"
            
            Servicios disponibles:
            {json.dumps(services_context, indent=2, ensure_ascii=False)}
            
            Contexto de conversación: {json.dumps(conversation_context or {}, ensure_ascii=False)}
            
            Responde en formato JSON con:
            {{
                "identified_service_id": "ID del servicio identificado o null",
                "confidence_score": "número del 0-100",
                "alternative_services": ["lista de IDs de servicios alternativos"],
                "required_parameters": ["parámetros requeridos para el servicio"],
                "missing_parameters": ["parámetros que faltan"],
                "clarification_needed": true/false,
                "clarification_questions": ["preguntas para aclarar"]
            }}
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en identificación de servicios. Analiza mensajes de clientes y identifica qué servicio necesitan con alta precisión."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            ai_result = json.loads(response.choices[0].message.content)
            
            identified_service = None
            if ai_result.get("identified_service_id"):
                identified_service = next(
                    (s for s in available_services if s.id == ai_result["identified_service_id"]),
                    None
                )
            
            alternative_services = [
                s for s in available_services 
                if s.id in ai_result.get("alternative_services", [])
            ]
            
            return ServiceIdentificationResponse(
                identified_service=identified_service,
                confidence_score=ai_result.get("confidence_score", 0),
                alternative_services=alternative_services,
                required_parameters=ai_result.get("required_parameters", []),
                missing_parameters=ai_result.get("missing_parameters", []),
                clarification_needed=ai_result.get("clarification_needed", False),
                clarification_questions=ai_result.get("clarification_questions", [])
            )
            
        except Exception as e:
            logger.error(f"Error in service identification: {e}")
            return ServiceIdentificationResponse(
                identified_service=None,
                confidence_score=0,
                alternative_services=[],
                required_parameters=[],
                missing_parameters=[],
                clarification_needed=True,
                clarification_questions=["¿Puedes describir con más detalle qué servicio necesitas?"]
            )
    
    async def extract_rfc(self, message_text: str) -> Optional[str]:
        """Extract RFC from message text"""
        
        rfc_pattern = r'\b[A-Z]{4}\d{6}[A-Z0-9]{3}\b'
        
        rfc_pattern_individual = r'\b[A-Z]{3}\d{6}[A-Z0-9]{3}\b'
        
        match = re.search(rfc_pattern, message_text.upper())
        if not match:
            match = re.search(rfc_pattern_individual, message_text.upper())
        
        if match:
            return match.group()
        
        try:
            prompt = f"""
            Extrae el RFC del siguiente mensaje. Un RFC mexicano tiene el formato:
            - Para empresas: 4 letras + 6 dígitos + 3 caracteres alfanuméricos
            - Para personas: 3 letras + 6 dígitos + 3 caracteres alfanuméricos
            
            Mensaje: "{message_text}"
            
            Responde solo con el RFC encontrado o "null" si no hay ninguno.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en identificación de RFCs mexicanos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            return result if result != "null" else None
            
        except Exception as e:
            logger.error(f"Error extracting RFC: {e}")
            return None
    
    async def extract_service_parameters(
        self,
        message_text: str,
        service_id: str,
        existing_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract service parameters from message"""
        
        try:
            prompt = f"""
            Extrae parámetros del servicio del siguiente mensaje del cliente.
            
            Mensaje: "{message_text}"
            Servicio ID: {service_id}
            Parámetros existentes: {json.dumps(existing_parameters, ensure_ascii=False)}
            
            Extrae información como:
            - Dirección o ubicación
            - Fecha y hora preferida
            - Detalles específicos del servicio
            - Urgencia o prioridad
            - Cualquier requisito especial
            
            Responde en formato JSON con los parámetros extraídos.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en extracción de información de servicios."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            return {}
    
    async def detect_confirmation(self, message_text: str) -> bool:
        """Detect if message contains confirmation"""
        
        confirmation_words = [
            "sí", "si", "yes", "confirmo", "acepto", "de acuerdo",
            "perfecto", "ok", "está bien", "correcto", "adelante"
        ]
        
        negative_words = [
            "no", "nope", "cancel", "cancelo", "mejor no", "no gracias"
        ]
        
        message_lower = message_text.lower()
        
        for word in confirmation_words:
            if word in message_lower:
                return True
        
        for word in negative_words:
            if word in message_lower:
                return False
        
        try:
            prompt = f"""
            ¿El siguiente mensaje indica confirmación o aceptación?
            
            Mensaje: "{message_text}"
            
            Responde solo "true" o "false".
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Determina si un mensaje indica confirmación o aceptación."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip().lower() == "true"
            
        except Exception as e:
            logger.error(f"Error detecting confirmation: {e}")
            return False
    
    async def analyze_sentiment(self, message_text: str) -> Dict[str, Any]:
        """Analyze message sentiment for escalation detection"""
        
        try:
            prompt = f"""
            Analiza el sentimiento del siguiente mensaje del cliente:
            
            Mensaje: "{message_text}"
            
            Responde en formato JSON:
            {{
                "sentiment": "positive/neutral/negative",
                "confidence": "número del 0-100",
                "frustration_level": "número del 0-100",
                "urgency_level": "número del 0-100",
                "escalation_recommended": true/false
            }}
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de sentimientos de servicio al cliente."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 50,
                "frustration_level": 0,
                "urgency_level": 0,
                "escalation_recommended": False
            }
    
    async def get_service(self, service_id: str) -> Optional[Any]:
        """Get service information (placeholder - should use service manager)"""
        
        return type('Service', (), {
            'id': service_id,
            'required_parameters': ['location', 'preferred_time']
        })()
