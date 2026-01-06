import uuid
from datetime import datetime

from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SAEnum

from .base import Base
from .enums import DeviceState


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=True,
    )

    fingerprint: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    state: Mapped[DeviceState] = mapped_column(
        SAEnum(DeviceState, name="device_state", native_enum=True),
        nullable=False,
        server_default=DeviceState.PENDING.value,
    )

    token_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    tenant = relationship("Tenant", back_populates="devices")
    screens = relationship("Screen", back_populates="device")
    heartbeats = relationship("DeviceHeartbeat", back_populates="device")
