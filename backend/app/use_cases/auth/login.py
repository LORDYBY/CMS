from app.infrastructure.db.repositories.user_repository import UserRepository
from app.common.security import verify_password
from app.infrastructure.auth.jwt import create_access_token


class LoginUseCase:

    def __init__(self, session):
        self.users = UserRepository(session)

    async def execute(self, *, tenant_id, email, password):
        user = await self.users.get_by_email(
            tenant_id=tenant_id,
            email=email
        )

        if not user or not user.is_active:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        token = create_access_token(
            subject=str(user.id),
            tenant_id=str(user.tenant_id)
        )

        return token
