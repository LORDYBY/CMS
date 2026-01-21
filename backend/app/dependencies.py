from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.settings import settings
from app.infrastructure.db.session import get_db
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.device import Device
from app.common.device_tokens import hash_device_token
from app.common.constants import SYSTEM_TENANT_ID

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
):
    token = credentials.credentials

    # ==== 1. Decode token ====
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGO],
        )
        user_id = payload.get("sub")
        token_tenant_id = payload.get("tenant_id")
        token_role = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ==== 2. Fetch user from DB ====
    # Validate with DB, NOT token alone (prevents hacking)
    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # ==== 3. Verify tenant match for normal users ====
    if user.tenant_id != SYSTEM_TENANT_ID:
        # Normal user → tenant MUST match JWT
        if str(user.tenant_id) != str(token_tenant_id):
            raise HTTPException(status_code=401, detail="Tenant mismatch")

    # ==== 4. Identify ROOT user ====
    user.is_root = (user.tenant_id == SYSTEM_TENANT_ID)

    # Optional: ensure DB and token agree on role
    if user.is_root and token_role != "ROOT":
        raise HTTPException(status_code=401, detail="Invalid token role")

    return user

# =========================
# DEVICE AUTH (WEBSOCKET)
# =========================
async def get_current_device_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_db),
):
    auth = websocket.headers.get("authorization")

    if not auth or not auth.startswith("Bearer "):
        raise WebSocketException(code=4401)

    token = auth.replace("Bearer ", "")
    token_hash = hash_device_token(token)

    result = await session.execute(
        select(Device).where(
            Device.token_hash == token_hash,
            Device.state == "ACTIVE",
        )
    )

    device = result.scalar_one_or_none()
    if not device:
        raise WebSocketException(code=4401)

    return device

# =========================
# ADMIN AUTH (WEBSOCKET)
# =========================
async def get_current_user_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_db),
):
    auth = websocket.headers.get("authorization")

    if not auth or not auth.startswith("Bearer "):
        raise WebSocketException(code=4401)

    token = auth.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGO]
        )
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")

    except JWTError:
        raise WebSocketException(code=4401)

    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_active.is_(True),
            User.deleted_at.is_(None)
        )
    )

    user = result.scalar_one_or_none()
    if not user:
        raise WebSocketException(code=4401)

    return user
# =========================
