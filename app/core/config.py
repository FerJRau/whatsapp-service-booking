from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "WhatsApp Service Booking"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str
    WHATSAPP_API_VERSION: str = "v18.0"
    
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    DATABASE_URL: str = "sqlite:///./whatsapp_booking.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    WEBHOOK_SECRET: str
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_CONCURRENT_SESSIONS: int = 1000
    
    SUPPLIER_RESPONSE_TIMEOUT_SECONDS: int = 300
    MAX_SUPPLIERS_PER_REQUEST: int = 5
    
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    DEFAULT_SERVICE_AREA_RADIUS_KM: int = 50
    EMERGENCY_RESPONSE_TIME_MINUTES: int = 15
    STANDARD_RESPONSE_TIME_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
