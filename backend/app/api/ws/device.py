# from fastapi import WebSocket, WebSocketDisconnect
# from datetime import timezone
# from sqlalchemy import select

# from app.common.device_tokens import hash_device_token
# from app.infrastructure.db.session import get_db
# from app.infrastructure.db.models.device import Device
# from app.infrastructure.redis.client import redis


# async def device_ws(websocket: WebSocket):
#     # 1️⃣ Accept connection FIRST
#     await websocket.accept()

#     # 2️⃣ Extract Authorization header
#     auth = websocket.headers.get("authorization")
#     if not auth or not auth.startswith("Bearer "):
#         await websocket.close(code=4401)
#         return

#     token = auth.replace("Bearer ", "")
#     token_hash = hash_device_token(token)

#     # 3️⃣ Authenticate device manually
#     async for session in get_db():
#         result = await session.execute(
#             select(Device).where(
#                 Device.token_hash == token_hash,
#                 Device.state == "ACTIVE",
#             )
#         )
#         device = result.scalar_one_or_none()
#         break

#     if not device:
#         await websocket.close(code=4401)
#         return

#     device_id = str(device.id)

#     # 4️⃣ Main loop
#     try:
#         while True:
#             # Presence heartbeat
#             await redis.setex(f"device:online:{device_id}", 60, "1")

#             # Keep connection alive
#             await websocket.receive_text()

#     except WebSocketDisconnect:
#         await redis.delete(f"device:online:{device_id}")
#         #

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.common.device_tokens import hash_device_token
from app.infrastructure.db.session import get_db
from app.infrastructure.db.models.device import Device
from app.infrastructure.redis.client import redis


async def device_ws(websocket: WebSocket):
    # ACCEPT FIRST
    await websocket.accept()

    auth = websocket.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        await websocket.close(code=4401)
        return

    token = auth.replace("Bearer ", "")
    token_hash = hash_device_token(token)

    async for session in get_db():
        result = await session.execute(
            select(Device).where(
                Device.token_hash == token_hash,
                Device.state == "ACTIVE",
            )
        )
        device = result.scalar_one_or_none()
        break

    if not device:
        await websocket.close(code=4401)
        return

    device_id = str(device.id)

    try:
        while True:
            await redis.setex(f"device:online:{device_id}", 60, "1")
            await websocket.receive_text()
    except WebSocketDisconnect:
        await redis.delete(f"device:online:{device_id}")
