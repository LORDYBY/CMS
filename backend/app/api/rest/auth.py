from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_db
from app.use_cases.auth.login import LoginUseCase
from app.api.schemas.auth import LoginRequest, LoginResponse
from app.use_cases.auth.root_login import RootLoginUseCase
from app.api.schemas.auth import RootLoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        token = await LoginUseCase(session).execute(
            tenant_id=payload.tenant_id,
            email=payload.email,
            password=payload.password,
        )

        return LoginResponse(access_token=token)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

@router.post("/root-login")
async def root_login(
    payload: RootLoginRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await RootLoginUseCase(session).execute(
            email=payload.email,
            password=payload.password,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )