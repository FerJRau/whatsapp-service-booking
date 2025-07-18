import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.message_processor import MessageProcessor
from app.core.database import AsyncSessionLocal

@pytest.fixture
async def db_session():
    """Create test database session"""
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
def message_processor(db_session):
    """Create message processor instance"""
    return MessageProcessor(db_session)

@pytest.mark.asyncio
async def test_extract_message_content(message_processor):
    """Test message content extraction"""
    
    text_message = {
        "type": "text",
        "text": {"body": "Necesito un plomero"}
    }
    content = await message_processor._extract_message_content(text_message)
    assert content == "Necesito un plomero"
    
    interactive_message = {
        "type": "interactive",
        "interactive": {
            "button_reply": {"title": "Confirmar"}
        }
    }
    content = await message_processor._extract_message_content(interactive_message)
    assert content == "Confirmar"
    
    media_message = {
        "type": "image"
    }
    content = await message_processor._extract_message_content(media_message)
    assert content == "[IMAGE] Media file received"

@pytest.mark.asyncio
async def test_process_message_flow(message_processor):
    """Test complete message processing flow"""
    
    message_processor.session_service = AsyncMock()
    message_processor.customer_service = AsyncMock()
    message_processor.whatsapp_service = AsyncMock()
    
    mock_session = MagicMock()
    mock_session.id = "test_session_id"
    mock_session.phone_number = "+525512345678"
    mock_session.current_step = "greeting"
    mock_session.is_expired = False
    mock_session.total_messages = 0
    
    message_processor.session_service.get_active_session_by_phone.return_value = mock_session
    message_processor.session_service.add_message.return_value = MagicMock()
    message_processor.session_service.update_session.return_value = mock_session
    
    mock_customer = MagicMock()
    mock_customer.rfc = "ABCD123456EF1"
    mock_customer.first_name = "Ana"
    message_processor.customer_service.get_customer_by_phone.return_value = mock_customer
    
    message_data = {
        "type": "text",
        "text": {"body": "Hola, necesito ayuda"},
        "id": "test_message_id"
    }
    
    webhook_value = {}
    
    await message_processor.process_message(
        phone_number="+525512345678",
        message_data=message_data,
        webhook_value=webhook_value
    )
    
    message_processor.session_service.add_message.assert_called_once()
    message_processor.whatsapp_service.send_text_message.assert_called_once()
    message_processor.whatsapp_service.mark_message_read.assert_called_once_with("test_message_id")

if __name__ == "__main__":
    pytest.main([__file__])
