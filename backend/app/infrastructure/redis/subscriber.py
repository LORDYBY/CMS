# import asyncio
# from app.infrastructure.redis import client
# from app.api.ws.connection_manager import manager


# async def redis_listener():
#     while client.redis is None:
#         await asyncio.sleep(0.1)

#     pubsub = client.redis.pubsub(ignore_subscribe_messages=True)
#     await pubsub.execute_command("SUBSCRIBE", "broadcast:emergency")

#     while True:
#         msg = await pubsub.get_message(timeout=1)
#         if msg:
#             data = msg["data"]
#             if isinstance(data, bytes):
#                 data = data.decode()
#             await manager.broadcast(data)

#         await asyncio.sleep(0.01)
###################################################
# import asyncio
# from app.infrastructure.redis import client
# from app.api.ws.connection_manager import manager

# CHANNEL = "broadcast:emergency"

# async def redis_listener():
#     # Wait for redis to be connected
#     while client.redis is None:
#         await asyncio.sleep(0.1)

#     pubsub = client.redis.pubsub(ignore_subscribe_messages=True)
#     await pubsub.subscribe(CHANNEL)

#     print(f">>> Redis subscriber listening on channel: {CHANNEL}")

#     async for message in pubsub.listen():
#         if message["type"] != "message":
#             continue

#         data = message["data"]
#         if isinstance(data, bytes):
#             data = data.decode()

#         print(">>> Redis subscriber received:", data)


#         # Send to WebSocket clients
#         await manager.broadcast(data)

#########################################

import asyncio
import json
from app.infrastructure.redis import client
from app.api.ws.connection_manager import manager

CHANNELS = [
    "broadcast:emergency",
    "broadcast:admin",
    "broadcast:command",
]


async def redis_listener():

    # Wait for redis to be connected
    while client.redis is None:
        print(">>> Redis listener waiting for redis client...")
        await asyncio.sleep(0.1)

    print(">>> Redis listener connected to Redis")

    # Create pubsub
    pubsub = client.redis.pubsub(ignore_subscribe_messages=True)

    # Subscribe to all channels
    await pubsub.subscribe(*CHANNELS)
    print(f">>> Subscribed to channels: {CHANNELS}")

    # Main loop
    while True:
        message = await pubsub.get_message(timeout=1)

        if message:
            channel = message["channel"]
            data = message["data"]

            # Decode data
            if isinstance(data, bytes):
                data = data.decode()

            print(f">>> Redis message on {channel}: {data}")

            # Broadcast to all WS connections
            await manager.broadcast(data)

        # short sleep to yield control
        await asyncio.sleep(0.01)