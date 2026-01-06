# import uuid
# from datetime import datetime
# from sqlalchemy import (
#     Column, Text, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint
# )
# from sqlalchemy.dialects.postgresql import UUID

# from app.infrastructure.db.models.base import Base


# class User(Base):
#     __tablename__ = "users"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

#     email = Column(Text, nullable=False)
#     password_hash = Column(Text, nullable=False)

#     is_active = Column(Boolean, nullable=False, default=True)

#     created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
#     deleted_at = Column(TIMESTAMP, nullable=True)

#     __table_args__ = (
#         UniqueConstraint("tenant_id", "email", name="uq_user_email_per_tenant"),
#     )

# user.py
import uuid
from datetime import datetime

from sqlalchemy import Text, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
