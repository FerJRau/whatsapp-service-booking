from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class WhatsAppContact(BaseModel):
    profile: Optional[Dict[str, str]] = None
    wa_id: str

class WhatsAppMessage(BaseModel):
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[Dict[str, str]] = None
    image: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    contacts: Optional[List[Dict[str, Any]]] = None

class WhatsAppChange(BaseModel):
    value: Dict[str, Any]
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[WhatsAppEntry]

class WhatsAppVerification(BaseModel):
    mode: str = Field(alias="hub.mode")
    token: str = Field(alias="hub.verify_token")
    challenge: str = Field(alias="hub.challenge")

class OutboundMessage(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: Optional[Dict[str, str]] = None
    template: Optional[Dict[str, Any]] = None
    interactive: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    messaging_product: str
    contacts: List[Dict[str, str]]
    messages: List[Dict[str, str]]
