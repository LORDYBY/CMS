import uuid
from datetime import datetime
from sqlalchemy import Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="ACTIVE",
        server_default="ACTIVE"
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()     # DATABASE generates value
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    locations = relationship("Location", back_populates="tenant")
    users = relationship("User", back_populates="tenant")
    roles = relationship("Role", back_populates="tenant")
    devices = relationship("Device", back_populates="tenant")