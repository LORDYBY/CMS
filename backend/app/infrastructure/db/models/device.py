# import uuid
# from datetime import datetime
# # from sqlalchemy import (
# #     Column, Text, TIMESTAMP, ForeignKey
# # )

# from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, Enum as SAEnum


# from sqlalchemy.dialects.postgresql import UUID

# from app.infrastructure.db.models.base import Base
# from app.domain.enums.device_state import DeviceState

# class Device(Base):
#     __tablename__ = "devices"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

#     tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

#     fingerprint = Column(Text, nullable=False, unique=True)

#     name = Column(Text, nullable=True)

#     #state = Column(Text, nullable=False, default="PENDING")
    
#     state = Column(
#     SAEnum(DeviceState, name="device_state", native_enum=True),
#     nullable=False,
#     default=DeviceState.PENDING,
#     )


#     token_hash = Column(Text, nullable=True)

#     approved_at = Column(TIMESTAMP, nullable=True)
#     revoked_at = Column(TIMESTAMP, nullable=True)

#     created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
#     last_seen_at = Column(TIMESTAMP, nullable=True)


# import uuid
# from datetime import datetime, timezone

# from sqlalchemy import Column, Text, ForeignKey, Enum as SAEnum, DateTime
# from sqlalchemy.dialects.postgresql import UUID

# from app.infrastructure.db.models.base import Base
# from app.domain.enums.device_state import DeviceState


# class Device(Base):
#     __tablename__ = "devices"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

#     tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

#     fingerprint = Column(Text, nullable=False, unique=True)

#     name = Column(Text, nullable=True)

#     state = Column(
#         SAEnum(DeviceState, name="device_state", native_enum=True),
#         nullable=False,
#         default=DeviceState.PENDING,
#     )

#     token_hash = Column(Text, nullable=True)

#     # ✅ timezone-aware timestamps
#     approved_at = Column(DateTime(timezone=True), nullable=True)
#     revoked_at = Column(DateTime(timezone=True), nullable=True)
#     last_seen_at = Column(DateTime(timezone=True), nullable=True)

#     created_at = Column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )
# ##


# device.py
from sqlalchemy import Column, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base
from .enums import DeviceState


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True))
    fingerprint = Column(Text, nullable=False, unique=True)
    name = Column(Text)
    state = Column(Enum(DeviceState, name="device_state"), nullable=False, server_default="PENDING")
    token_hash = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True))

