from app.common.constants import SYSTEM_TENANT_ID
from app.infrastructure.auth.jwt import create_access_token
from app.common.security import verify_password
from app.infrastructure.db.repositories.user_repository import UserRepository

class RootLoginUseCase:

    def __init__(self, session):
        self.users = UserRepository(session)

    async def execute(self, *, email, password):
        user = await self.users.get_by_email(
            tenant_id=SYSTEM_TENANT_ID,
            email=email
        )

        if not user or not user.is_active:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        token = create_access_token(
            subject=str(user.id),
            tenant_id=str(SYSTEM_TENANT_ID),
            role="ROOT"
        )

        return {"access_token": token}
    
