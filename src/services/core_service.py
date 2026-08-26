import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import AuditLog, Notification

logger = logging.getLogger(__name__)


class CoreValidationError(ValueError):
    """Raised when audit or notification input is invalid."""


class CoreService:
    def record_audit(
        self,
        session: Session,
        tenant_id: str,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            tenant_id=self._required_text(tenant_id, "tenant_id", 100),
            actor_id=self._required_text(actor_id, "actor_id", 100),
            action=self._required_text(action, "action", 100),
            resource_type=self._required_text(resource_type, "resource_type", 100),
            resource_id=self._required_text(resource_id, "resource_id", 100),
            details=details or {},
        )
        session.add(audit_log)
        session.commit()
        logger.info(
            "audit_recorded",
            extra={"tenant_id": tenant_id, "actor_id": actor_id, "action": action},
        )
        return audit_log

    def get_audit_logs(
        self, session: Session, tenant_id: str, limit: int = 100
    ) -> list[AuditLog]:
        self._validate_limit(limit)
        return list(
            session.scalars(
                select(AuditLog)
                .where(AuditLog.tenant_id == self._required_text(tenant_id, "tenant_id", 100))
                .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
                .limit(limit)
            )
        )

    def create_notification(
        self,
        session: Session,
        tenant_id: str,
        recipient_id: str,
        notification_type: str,
        message: str,
    ) -> Notification:
        notification = Notification(
            tenant_id=self._required_text(tenant_id, "tenant_id", 100),
            recipient_id=self._required_text(recipient_id, "recipient_id", 100),
            notification_type=self._required_text(notification_type, "notification_type", 100),
            message=self._required_text(message, "message", 500),
        )
        session.add(notification)
        session.commit()
        logger.info(
            "notification_created",
            extra={"tenant_id": tenant_id, "recipient_id": recipient_id},
        )
        return notification

    def get_notifications(
        self,
        session: Session,
        tenant_id: str,
        recipient_id: str,
        limit: int = 100,
    ) -> list[Notification]:
        self._validate_limit(limit)
        return list(
            session.scalars(
                select(Notification)
                .where(
                    Notification.tenant_id == self._required_text(tenant_id, "tenant_id", 100),
                    Notification.recipient_id
                    == self._required_text(recipient_id, "recipient_id", 100),
                )
                .order_by(Notification.created_at.desc(), Notification.id.desc())
                .limit(limit)
            )
        )

    def mark_notification_read(
        self, session: Session, tenant_id: str, recipient_id: str, notification_id: int
    ) -> Notification:
        notification = session.scalar(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.tenant_id == self._required_text(tenant_id, "tenant_id", 100),
                Notification.recipient_id
                == self._required_text(recipient_id, "recipient_id", 100),
            )
        )
        if notification is None:
            raise LookupError("Notification not found")
        notification.is_read = True
        session.commit()
        return notification

    @staticmethod
    def _required_text(value: str, field_name: str, max_length: int) -> str:
        clean_value = value.strip()
        if not clean_value or len(clean_value) > max_length:
            raise CoreValidationError(
                f"{field_name} must be between 1 and {max_length} characters"
            )
        return clean_value

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if not 1 <= limit <= 500:
            raise CoreValidationError("limit must be between 1 and 500")