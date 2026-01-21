# # from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
# # from sqlalchemy import select
# # from sqlalchemy.ext.asyncio import AsyncSession

# # import app.infrastructure.redis.client as redis_client
# # from app.common.device_tokens import hash_device_token
# # from app.infrastructure.db.session import get_db
# # from app.infrastructure.db.models.device import Device

# # router = APIRouter()


# # async def authenticate_device(websocket: WebSocket, session: AsyncSession):
# #     auth = websocket.headers.get("authorization")
# #     if not auth or not auth.startswith("Bearer "):
# #         raise WebSocketException(code=4401)

# #     token = auth.replace("Bearer ", "")
# #     token_hash = hash_device_token(token)

# #     result = await session.execute(
# #         select(Device).where(
# #             Device.token_hash == token_hash,
# #             Device.state == "ACTIVE",
# #         )
# #     )
# #     device = result.scalar_one_or_none()

# #     if not device:
# #         raise WebSocketException(code=4401)

# #     return device


# # @router.websocket("/device")
# # async def device_ws(
# #     websocket: WebSocket,
# #     session: AsyncSession = Depends(get_db),
# # ):
# #     await websocket.accept()

# #     try:
# #         device = await authenticate_device(websocket, session)
# #     except WebSocketException as e:
# #         await websocket.close(code=e.code)
# #         return

# #     device_id = str(device.id)

# #     # Mark online immediately
# #     await redis_client.redis.setex(f"device:online:{device_id}", 60, "1")

# #     try:
# #         while True:
# #             # Refresh TTL
# #             await redis_client.redis.setex(f"device:online:{device_id}", 60, "1")

# #             # Keep the connection alive
# #             await websocket.receive_text()

# #     except WebSocketDisconnect:
# #         # Mark offline
# #         await redis_client.redis.delete(f"device:online:{device_id}")
# #     finally:
# #         await websocket.close()
# ####################################################################################

# # from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
# # from sqlalchemy import select
# # from sqlalchemy.ext.asyncio import AsyncSession
# # import asyncio
# # import json

# # import app.infrastructure.redis.client as redis_client
# # from app.common.device_tokens import hash_device_token
# # from app.infrastructure.db.session import get_db
# # from app.infrastructure.db.models.device import Device

# # router = APIRouter()


# # async def authenticate_device(websocket: WebSocket, session: AsyncSession):
# #     auth = websocket.headers.get("authorization")
# #     if not auth or not auth.startswith("Bearer "):
# #         raise WebSocketException(code=4401)

# #     token = auth.replace("Bearer ", "")
# #     token_hash = hash_device_token(token)

# #     result = await session.execute(
# #         select(Device).where(
# #             Device.token_hash == token_hash,
# #             Device.state == "ACTIVE",
# #         )
# #     )
# #     device = result.scalar_one_or_none()

# #     if not device:
# #         raise WebSocketException(code=4401)

# #     return device


# # @router.websocket("/device")
# # async def device_ws(
# #     websocket: WebSocket,
# #     session: AsyncSession = Depends(get_db),
# # ):
# #     await websocket.accept()

# #     try:
# #         device = await authenticate_device(websocket, session)
# #     except WebSocketException as e:
# #         await websocket.close(code=e.code)
# #         return

# #     device_id = str(device.id)

# #     # Mark online
# #     await redis_client.redis.setex(f"device:online:{device_id}", 60, "1")

# #     # Subscribe to commands
# #     pubsub = redis_client.redis.pubsub()
# #     await pubsub.subscribe(f"device:commands:{device_id}")

# #     async def ws_reader():
# #         """WebSocket reads ONLY."""
# #         try:
# #             return await websocket.receive_text()
# #         except WebSocketDisconnect:
# #             return "disconnect"

# #     async def redis_reader():
# #         """Redis reads ONLY."""
# #         msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
# #         return msg

# #     try:
# #         while True:
# #             await redis_client.redis.setex(f"device:online:{device_id}", 60, "1")

# #             ws_task = asyncio.create_task(ws_reader())
# #             redis_task = asyncio.create_task(redis_reader())

# #             done, pending = await asyncio.wait(
# #                 {ws_task, redis_task},
# #                 return_when=asyncio.FIRST_COMPLETED,
# #             )

# #             # cancel the task that did NOT finish
# #             for p in pending:
# #                 p.cancel()

# #             result = list(done)[0].result()

# #             # Case 1: Device WS disconnected
# #             if result == "disconnect":
# #                 break

# #             # Case 2: Redis message
# #             if isinstance(result, dict) and result.get("data"):
# #                 try:
# #                     command = json.loads(result["data"])
# #                     await websocket.send_json(command)
# #                 except Exception:
# #                     pass
# #                 continue

# #             # Case 3: device sent keepalive
# #             # ignore result (string)
# #             continue

# #     except Exception as e:
# #         print("DEVICE WS ERROR:", e)

# #     finally:
# #         await redis_client.redis.delete(f"device:online:{device_id}")
# #         await websocket.close()

# ####################################################################################

# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# import asyncio
# import json

# import app.infrastructure.redis.client as redis_client
# from app.common.device_tokens import hash_device_token
# from app.infrastructure.db.session import get_db
# from app.infrastructure.db.models.device import Device


# router = APIRouter()


# # ---------------------------------------------------------
# # AUTHENTICATION (header + query param)
# # ---------------------------------------------------------
# async def authenticate_device(websocket: WebSocket, session: AsyncSession):
#     print("WS AUTH → starting")
#     print("Headers:", websocket.headers)
#     print("Query params:", websocket.query_params)

#     token = None

#     # Try header
#     auth_header = websocket.headers.get("authorization")
#     if auth_header:
#         print("WS AUTH → header received:", auth_header)
#     if auth_header and auth_header.startswith("Bearer "):
#         token = auth_header[len("Bearer "):].strip()

#     # Try query param
#     if not token:
#         token = websocket.query_params.get("token")
#         print("WS AUTH → query token:", token)

#     if not token:
#         print("WS AUTH → no token provided")
#         raise WebSocketException(code=4401)

#     token_hash = hash_device_token(token)
#     print("WS AUTH → token hash:", token_hash)

#     result = await session.execute(
#         select(Device).where(
#             Device.token_hash == token_hash,
#             Device.state == "ACTIVE",
#         )
#     )
#     device = result.scalar_one_or_none()

#     if not device:
#         print("WS AUTH → no matching device found!")
#         raise WebSocketException(code=4401)

#     print("WS AUTH → success:", device.id)
#     return device


# # ---------------------------------------------------------
# # DEVICE WEBSOCKET HANDLER
# # ---------------------------------------------------------
# @router.websocket("/device")
# async def device_ws(
#     websocket: WebSocket,
#     session: AsyncSession = Depends(get_db),
# ):
#     # Accept WS first (required by FastAPI)
#     await websocket.accept()

#     # -----------------------------
#     # AUTHENTICATION
#     # -----------------------------
#     try:
#         device = await authenticate_device(websocket, session)
#     except WebSocketException as e:
#         await websocket.close(code=e.code)
#         return

#     device_id = str(device.id)

#     # -----------------------------
#     # ONLINE STATUS
#     # -----------------------------
#     await redis_client.redis.setex(f"device:online:{device_id}", 60, "1")

#     # -----------------------------
#     # SUBSCRIBE TO REDIS COMMANDS
#     # -----------------------------
#     pubsub = redis_client.redis.pubsub()
#     await pubsub.subscribe(f"device:commands:{device_id}")

#     async def ws_reader():
#         """Reads messages from WebSocket."""
#         try:
#             return await websocket.receive_text()
#         except WebSocketDisconnect:
#             return "disconnect"

#     async def redis_reader():
#         """Reads messages from Redis."""
#         msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
#         return msg

#     try:
#         while True:
#             # Refresh presence TTL
#             await redis_client.redis.setex(f"device:online:{device_id}", 60, "1")

#             # Wait for WebSocket OR Redis message
#             ws_task = asyncio.create_task(ws_reader())
#             redis_task = asyncio.create_task(redis_reader())

#             done, pending = await asyncio.wait(
#                 {ws_task, redis_task},
#                 return_when=asyncio.FIRST_COMPLETED,
#             )

#             for p in pending:
#                 p.cancel()

#             event = list(done)[0].result()

#             # -----------------------------
#             # DEVICE DISCONNECTED
#             # -----------------------------
#             if event == "disconnect":
#                 break

#             # -----------------------------
#             # REDIS COMMAND RECEIVED
#             # -----------------------------
#             if isinstance(event, dict) and event.get("data"):
#                 try:
#                     cmd = json.loads(event["data"])
#                     await websocket.send_json(cmd)
#                 except:
#                     pass
#                 continue

#             # -----------------------------
#             # DEVICE SENT KEEPALIVE MESSAGE
#             # -----------------------------
#             continue

#     except Exception as e:
#         print("WEBSOCKET ERROR:", e)

#     finally:
#         # IMPORTANT: DO NOT manually close websocket here
#         await redis_client.redis.delete(f"device:online:{device_id}")
#         try:
#             await pubsub.unsubscribe(f"device:commands:{device_id}")
#         except:
#             pass
#         # FastAPI will auto-close WS on exit


# ####################################################################################


# app/api/ws/device.py
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# import asyncio, json

# from app.common.device_tokens import hash_device_token
# from app.infrastructure.db.session import get_db
# from app.infrastructure.db.models.device import Device
# import app.infrastructure.redis.client as redis_client

# router = APIRouter()


# async def authenticate_device(websocket: WebSocket, session: AsyncSession):
#     print("WS AUTH → starting")
#     print("Headers:", websocket.headers)
#     print("Query params:", websocket.query_params)

#     token = websocket.query_params.get("token")
#     if not token:
#         raise WebSocketException(code=4401)

#     print("WS AUTH → query token:", token)

#     token_hash = hash_device_token(token)
#     print("WS AUTH → token hash:", token_hash)

#     result = await session.execute(
#         select(Device).where(Device.token_hash == token_hash)
#     )
#     device = result.scalar_one_or_none()

#     if not device:
#         print("WS AUTH → no matching device found!")
#         raise WebSocketException(code=4401)

#     print("WS AUTH → authenticated device:", device.id)
#     return device


# @router.websocket("/device")
# async def device_ws(websocket: WebSocket, session: AsyncSession = Depends(get_db)):
#     await websocket.accept()

#     try:
#         device = await authenticate_device(websocket, session)
#     except WebSocketException as e:
#         await websocket.close(code=e.code)
#         return

#     device_id = str(device.id)

#     pubsub = redis_client.redis.pubsub()
#     await pubsub.subscribe(f"device:commands:{device_id}")

#     try:
#         while True:
#             msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
#             if msg and "data" in msg:
#                 try:
#                     cmd = json.loads(msg["data"])
#                     await websocket.send_json(cmd)
#                 except:
#                     pass
#     except WebSocketDisconnect:
#         pass
#     finally:
#         await websocket.close()




###########################################




from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio

from app.common.device_tokens import hash_device_token
from app.infrastructure.db.session import get_db
from app.infrastructure.db.models.device import Device
import app.infrastructure.redis.client as redis_client

router = APIRouter()


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------
async def authenticate_device(websocket: WebSocket, session: AsyncSession):
    token = websocket.query_params.get("token")
    if not token:
        raise WebSocketException(code=4401)

    token_hash = hash_device_token(token)

    result = await session.execute(
        select(Device).where(
            Device.token_hash == token_hash,
            Device.state == "APPROVED",
        )
    )
    device = result.scalar_one_or_none()

    if not device:
        raise WebSocketException(code=4401)

    return device


# ---------------------------------------------------------
# DEVICE WEBSOCKET (REDIS → WS ONLY)
# ---------------------------------------------------------
@router.websocket("/device")
async def device_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_db),
):
    await websocket.accept()

    try:
        device = await authenticate_device(websocket, session)
    except WebSocketException as e:
        await websocket.close(code=e.code)
        return

    device_id = str(device.id)

    pubsub = redis_client.redis.pubsub()
    await pubsub.subscribe(f"device:commands:{device_id}")

    try:
        while True:
            # Poll Redis (non-blocking)
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1
            )

            if message and message.get("data"):
                try:
                    command = json.loads(message["data"])
                    await websocket.send_json(command)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    print("WS SEND ERROR:", e)

            # Yield control (important)
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        pass

    finally:
        try:
            await pubsub.unsubscribe(f"device:commands:{device_id}")
        except Exception:
            pass
        await websocket.close()
