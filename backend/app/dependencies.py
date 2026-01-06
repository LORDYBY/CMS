# from fastapi import Depends, HTTPException, status
# from jose import jwt, JWTError
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from fastapi import Header

# from app.settings import settings
# from app.infrastructure.db.session import get_db
# from app.infrastructure.db.models.user import User
# from app.common.device_tokens import hash_device_token
# from app.infrastructure.db.models.device import Device


# async def get_current_user(
#     token: str = Depends(lambda: None),
#     session: AsyncSession = Depends(get_db),
# ):
#     if not token:
#         raise HTTPException(status_code=401, detail="Missing token")

#     try:
#         payload = jwt.decode(
#             token,
#             settings.JWT_SECRET,
#             algorithms=[settings.JWT_ALGO],
#         )
#         user_id = payload.get("sub")
#         tenant_id = payload.get("tenant_id")

#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     result = await session.execute(
#         select(User).where(
#             User.id == user_id,
#             User.tenant_id == tenant_id,
#             User.is_active.is_(True),
#             User.deleted_at.is_(None),
#         )
#     )

#     user = result.scalar_one_or_none()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")

#     return user

# async def get_current_device(
#     authorization: str = Header(...),
#     session: AsyncSession = Depends(get_db),
# ):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid auth header")

#     token = authorization.replace("Bearer ", "")
#     token_hash = hash_device_token(token)

#     result = await session.execute(
#         select(Device).where(
#             Device.token_hash == token_hash,
#             Device.state == "ACTIVE"
#         )
#     )

#     device = result.scalar_one_or_none()
#     if not device:
#         raise HTTPException(status_code=401, detail="Invalid device token")

#     return device



# from fastapi import Depends, HTTPException, status,WebSocket, WebSocketException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import jwt, JWTError
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select


# from app.settings import settings
# from app.infrastructure.db.session import get_db
# from app.infrastructure.db.models.user import User
# #####
# from app.common.device_tokens import hash_device_token
# from app.infrastructure.db.session import async_session
# from app.infrastructure.db.models.device import Device

# security = HTTPBearer()


# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     session: AsyncSession = Depends(get_db),
# ):
#     #print(">>> AUTH DEPENDENCY HIT")                     # DEBUG 1
#     #print(">>> RAW TOKEN:", credentials.credentials)    # DEBUG 2

#     token = credentials.credentials

#     try:
#         payload = jwt.decode(
#             token,
#             settings.JWT_SECRET,
#             algorithms=[settings.JWT_ALGO],
#         )
#        # print(">>> JWT PAYLOAD:", payload)               # DEBUG 3

#         user_id = payload.get("sub")
#         tenant_id = payload.get("tenant_id")

#     except JWTError as e:
#         #print(">>> JWT ERROR:", str(e))                  # DEBUG 4
#         raise HTTPException(status_code=401, detail="Invalid token")

#     result = await session.execute(
#         select(User).where(
#             User.id == user_id,
#             User.tenant_id == tenant_id,
#             User.is_active.is_(True),
#             User.deleted_at.is_(None),
#         )
#     )

#     user = result.scalar_one_or_none()
#     #print(">>> USER FOUND:", user)                       # DEBUG 5

#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")

#     return user

# async def get_current_device_ws(websocket: WebSocket):
#     auth = websocket.headers.get("authorization")

#     if not auth or not auth.startswith("Bearer "):
#         raise WebSocketException(code=4401)

#     token = auth.replace("Bearer ", "")
#     token_hash = hash_device_token(token)

#     async with async_session() as session:
#         result = await session.execute(
#             select(Device).where(
#                 Device.token_hash == token_hash,
#                 Device.state == "ACTIVE"
#             )
#         )
#         device = result.scalar_one_or_none()

#     if not device:
#         raise WebSocketException(code=4401)

#     return device


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

security = HTTPBearer()


# =========================
# USER AUTH (HTTP)
# =========================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGO],
        )
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
    )

    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

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
async def get_current_user_ws(websocket: WebSocket):
    auth = websocket.headers.get("authorization")

    if not auth or not auth.startswith("Bearer "):
        raise WebSocketException(code=4401)

    token = auth.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGO],
        )
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
    except JWTError:
        raise WebSocketException(code=4401)

    async for session in get_db():
        result = await session.execute(
            select(User).where(
                User.id == user_id,
                User.tenant_id == tenant_id,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        user = result.scalar_one_or_none()
        break

    if not user:
        raise WebSocketException(code=4401)

    return user
# =========================
