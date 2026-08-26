from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogCreate(BaseModel):
    actor_id: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    resource_type: str = Field(min_length=1, max_length=100)
    resource_id: str = Field(min_length=1, max_length=100)
    details: dict[str, Any] = Field(default_factory=dict)


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any]
    created_at: datetime


class NotificationCreate(BaseModel):
    recipient_id: str = Field(min_length=1, max_length=100)
    notification_type: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=500)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: str
    recipient_id: str
    notification_type: str
    message: str
    is_read: bool
    created_at: datetime