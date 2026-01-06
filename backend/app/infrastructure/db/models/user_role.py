# from sqlalchemy import Column, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID

# from app.infrastructure.db.models.base import Base


# class UserRole(Base):
#     __tablename__ = "user_roles"

#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
#     role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)


# user_role.py
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
