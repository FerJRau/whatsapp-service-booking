from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import verify_webhook_signature
from app.schemas.whatsapp import WhatsAppWebhook, WhatsAppVerification
from app.services.whatsapp import WhatsAppService
from app.services.message_processor import MessageProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
) -> PlainTextResponse:
    """Verify WhatsApp webhook"""
    
    if not all([hub_mode, hub_verify_token, hub_challenge]):
        logger.warning("Missing webhook verification parameters")
        raise HTTPException(status_code=400, detail="Missing verification parameters")
    
    if hub_mode != "subscribe":
        logger.warning(f"Invalid hub mode: {hub_mode}")
        raise HTTPException(status_code=400, detail="Invalid hub mode")
    
    if hub_verify_token != settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.warning("Invalid webhook verify token")
        raise HTTPException(status_code=403, detail="Invalid verify token")
    
    logger.info("Webhook verification successful")
    return PlainTextResponse(content=hub_challenge)

@router.post("/whatsapp")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Receive WhatsApp webhook messages"""
    
    try:
        body = await request.body()
        
        if not verify_webhook_signature(request, body):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        webhook_data = await request.json()
        logger.info(f"Received webhook: {webhook_data}")
        
        background_tasks.add_task(
            process_webhook_message,
            webhook_data,
            db
        )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def process_webhook_message(webhook_data: Dict[str, Any], db: AsyncSession):
    """Process incoming WhatsApp message"""
    
    try:
        webhook = WhatsAppWebhook(**webhook_data)
        
        for entry in webhook.entry:
            for change in entry.changes:
                if change.field == "messages":
                    value = change.value
                    
                    if "messages" in value:
                        for message_data in value["messages"]:
                            await process_incoming_message(message_data, value, db)
                    
                    if "statuses" in value:
                        for status_data in value["statuses"]:
                            await process_message_status(status_data, db)
                            
    except Exception as e:
        logger.error(f"Error processing webhook message: {e}", exc_info=True)

async def process_incoming_message(
    message_data: Dict[str, Any], 
    value: Dict[str, Any], 
    db: AsyncSession
):
    """Process individual incoming message"""
    
    try:
        phone_number = message_data.get("from")
        message_type = message_data.get("type")
        message_id = message_data.get("id")
        
        logger.info(f"Processing message from {phone_number}, type: {message_type}")
        
        processor = MessageProcessor(db)
        
        await processor.process_message(
            phone_number=phone_number,
            message_data=message_data,
            webhook_value=value
        )
        
    except Exception as e:
        logger.error(f"Error processing incoming message: {e}", exc_info=True)

async def process_message_status(status_data: Dict[str, Any], db: AsyncSession):
    """Process message delivery status updates"""
    
    try:
        message_id = status_data.get("id")
        status = status_data.get("status")
        
        logger.info(f"Message {message_id} status: {status}")
        
        
    except Exception as e:
        logger.error(f"Error processing message status: {e}", exc_info=True)
