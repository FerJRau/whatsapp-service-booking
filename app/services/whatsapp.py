import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for WhatsApp Business API integration"""
    
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        
    async def send_message(
        self, 
        to: str, 
        message_type: str = "text",
        content: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send message via WhatsApp Business API"""
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": message_type
        }
        
        if message_type == "text" and content:
            payload["text"] = {"body": content.get("body", "")}
        elif message_type == "template" and content:
            payload["template"] = content
        elif message_type == "interactive" and content:
            payload["interactive"] = content
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Message sent successfully to {to}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise
    
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send simple text message"""
        return await self.send_message(
            to=to,
            message_type="text",
            content={"body": text}
        )
    
    async def send_template_message(
        self, 
        to: str, 
        template_name: str,
        language_code: str = "es",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send template message"""
        
        template_content = {
            "name": template_name,
            "language": {"code": language_code}
        }
        
        if parameters:
            template_content["components"] = parameters
        
        return await self.send_message(
            to=to,
            message_type="template",
            content=template_content
        )
    
    async def send_interactive_message(
        self,
        to: str,
        interactive_type: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send interactive message (buttons, lists, etc.)"""
        
        interactive_content = {
            "type": interactive_type,
            **content
        }
        
        return await self.send_message(
            to=to,
            message_type="interactive",
            content=interactive_content
        )
    
    async def mark_message_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to mark message as read: {e}")
            raise
    
    async def get_media(self, media_id: str) -> Dict[str, Any]:
        """Get media file information"""
        
        url = f"{self.base_url}/{media_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get media info: {e}")
            raise
    
    async def download_media(self, media_url: str) -> bytes:
        """Download media file"""
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(media_url, headers=headers)
                response.raise_for_status()
                return response.content
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to download media: {e}")
            raise
