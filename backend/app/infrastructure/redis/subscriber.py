import asyncio
from app.infrastructure.redis import client
from app.api.ws.connection_manager import manager


async def redis_listener():
    while client.redis is None:
        await asyncio.sleep(0.1)

    pubsub = client.redis.pubsub(ignore_subscribe_messages=True)
    await pubsub.execute_command("SUBSCRIBE", "broadcast:emergency")

    while True:
        msg = await pubsub.get_message(timeout=1)
        if msg:
            data = msg["data"]
            if isinstance(data, bytes):
                data = data.decode()
            await manager.broadcast(data)

        await asyncio.sleep(0.01)
