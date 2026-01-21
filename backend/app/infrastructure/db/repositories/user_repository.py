from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.user import User


class UserRepository:

    def __init__(self, session):
        self.session = session

    async def get_by_email(self, tenant_id, email):
        stmt = (
            select(User)
            .options(
                selectinload(User.roles)  # PRELOAD ROLES (IMPORTANT)
            )
            .where(
                User.tenant_id == tenant_id,
                User.email == email,
                User.deleted_at.is_(None)
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

