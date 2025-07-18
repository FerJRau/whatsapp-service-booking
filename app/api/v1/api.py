from fastapi import APIRouter
from app.api.v1.endpoints import webhook, customers, services, suppliers, bookings, sessions

api_router = APIRouter()

api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
