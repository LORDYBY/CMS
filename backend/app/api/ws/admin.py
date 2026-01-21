from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import app.infrastructure.redis.client as redis_client

from app.dependencies import get_current_user_ws   # we will add this next
from app.infrastructure.db.session import get_db

router = APIRouter()

connected_admins = set()


@router.websocket("/admin")
async def admin_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_ws),
):
    await websocket.accept()

    admin_id = str(user.id)
    connected_admins.add(websocket)

    print(f">>> ADMIN CONNECTED: {admin_id}")

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            # Broadcast admin messages through Redis
            await redis_client.redis.publish(
                "broadcast:admin",
                json.dumps({
                    "admin_id": admin_id,
                    "msg": msg
                })
            )

    except WebSocketDisconnect:
        print(f">>> ADMIN DISCONNECTED: {admin_id}")

    finally:
        connected_admins.discard(websocket)
        await websocket.close()

