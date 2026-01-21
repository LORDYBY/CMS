# from redis.asyncio import Redis
# from app.settings import settings

# redis: Redis | None = None

# async def connect_redis():
#     global redis
#     redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

# async def disconnect_redis():
#     global redis
#     if redis:
#         await redis.close()


### Usage Example:
#client.py (redis)
from redis.asyncio import Redis
from app.settings import settings

redis: Redis | None = None


async def connect_redis():
    global redis
    print(">>> CONNECT_REDIS: starting")
    print(">>> CONNECT_REDIS: URL =", settings.REDIS_URL)

    redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=False,
    )

    pong = await redis.ping()
    print(">>> CONNECT_REDIS: PING =", pong)


async def disconnect_redis():
    global redis
    print(">>> DISCONNECT_REDIS")

    if redis:
        await redis.close()
        redis = None