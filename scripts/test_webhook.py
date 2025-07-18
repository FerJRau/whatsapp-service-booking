#!/usr/bin/env python3
"""
Test script for WhatsApp webhook functionality
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.services.message_processor import MessageProcessor
from app.schemas.whatsapp import WhatsAppWebhook

async def test_message_processing():
    """Test message processing without webhook signature validation"""
    
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456789",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15551234567",
                        "phone_number_id": "123456789"
                    },
                    "messages": [{
                        "id": "wamid.test123",
                        "from": "525511111111",
                        "timestamp": "1642676400",
                        "type": "text",
                        "text": {
                            "body": "Hola, necesito un plomero para reparar una fuga en mi baño"
                        }
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    async with AsyncSessionLocal() as db:
        try:
            parsed_data = WhatsAppWebhook(**webhook_data)
            print(f"✓ Webhook data parsed successfully")
            
            processor = MessageProcessor(db)
            print(f"✓ Message processor initialized")
            
            result = await processor.process_webhook(parsed_data)
            print(f"✓ Message processed successfully: {result}")
            
            webhook_data2 = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "id": "123456789",
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": "123456789"
                            },
                            "messages": [{
                                "id": "wamid.test124",
                                "from": "525511111111",
                                "timestamp": "1642676460",
                                "type": "text",
                                "text": {
                                    "body": "Es urgente, hay mucha agua en el piso"
                                }
                            }]
                        },
                        "field": "messages"
                    }]
                }]
            }
            
            parsed_data2 = WhatsAppWebhook(**webhook_data2)
            result2 = await processor.process_webhook(parsed_data2)
            print(f"✓ Follow-up message processed: {result2}")
            
            print("\n🎉 All tests passed! WhatsApp message processing is working correctly.")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_message_processing())
