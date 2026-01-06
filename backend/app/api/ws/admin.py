from fastapi import WebSocket
import json

from app.dependencies import get_current_user_ws
from app.infrastructure.redis.client import redis


async def admin_ws(websocket: WebSocket):
    user = await get_current_user_ws(websocket)
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            payload = json.loads(message)

            await redis.publish(
                payload["channel"],
                json.dumps(payload["data"])
            )
    except Exception:
        pass
