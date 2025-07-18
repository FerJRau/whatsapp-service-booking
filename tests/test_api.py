import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data

@pytest.mark.asyncio
async def test_webhook_verification():
    """Test WhatsApp webhook verification"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "demo_verify_token_replace_with_real",
                "hub.challenge": "test_challenge"
            }
        )
        assert response.status_code == 200
        assert response.text == "test_challenge"

@pytest.mark.asyncio
async def test_services_endpoint():
    """Test services listing endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/services/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

if __name__ == "__main__":
    pytest.main([__file__])
