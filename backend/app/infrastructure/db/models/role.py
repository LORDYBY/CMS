# import uuid
# from datetime import datetime
# from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, UniqueConstraint
# from sqlalchemy.dialects.postgresql import UUID

# from app.infrastructure.db.models.base import Base


# class Role(Base):
#     __tablename__ = "roles"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

#     name = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

#     __table_args__ = (
#         UniqueConstraint("tenant_id", "name", name="uq_role_name_per_tenant"),
#     )

# role.py
from sqlalchemy import Column, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="roles_tenant_id_name_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
