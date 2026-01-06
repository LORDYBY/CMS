# from sqlalchemy import Column, Text, TIMESTAMP
# from sqlalchemy.dialects.postgresql import UUID
# from app.infrastructure.db.models.base import Base
# import uuid
# from datetime import datetime

# class Tenant(Base):
#     __tablename__ = "tenants"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)


# import uuid
# from datetime import datetime
# from sqlalchemy import Column, Text, TIMESTAMP
# from sqlalchemy.dialects.postgresql import UUID

# from app.infrastructure.db.models.base import Base

# class Tenant(Base):
#     __tablename__ = "tenants"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(Text, nullable=False)
#     status = Column(Text, nullable=False, default="ACTIVE")

#     created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
#     deleted_at = Column(TIMESTAMP, nullable=True)


# tenant.py
from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default="ACTIVE")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))
