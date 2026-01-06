from sqlalchemy import Column, Text, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, BIGINT
from sqlalchemy.sql import func

from .base import Base
from .enums import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_tenant_time", "tenant_id", "created_at"),
    )

    id = Column(BIGINT, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True))
    actor_device_id = Column(UUID(as_uuid=True))
    action = Column(Enum(AuditAction, name="audit_action"), nullable=False)
    entity_type = Column(Text, nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
