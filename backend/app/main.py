# from fastapi import FastAPI
# from app.settings import settings
# from app.logging import setup_logging
# from app.infrastructure.redis.client import connect_redis, disconnect_redis
# from app.api.rest import router as api_router

# def create_app() -> FastAPI:
#     setup_logging()

#     app = FastAPI(
#         title="Digital Signage Backend",
#         version="1.0.0",
#     )

#     app.include_router(api_router, prefix="/api/v1")

#     @app.on_event("startup")
#     async def startup():
#         await connect_redis()

#     @app.on_event("shutdown")
#     async def shutdown():
#         await disconnect_redis()

#     return app

# # @app.get("/health")
# # async def health():
# #     return {"status": "ok"}

# app = create_app()



#######


from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.logging import setup_logging
from app.infrastructure.redis.client import connect_redis, disconnect_redis
from app.infrastructure.redis.subscriber import redis_listener
from app.api.rest import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ======================
    # STARTUP
    # ======================
    print(">>> LIFESPAN: startup begin")

    setup_logging()
    print(">>> LIFESPAN: logging ready")

    await connect_redis()
    print(">>> LIFESPAN: redis connected")

    redis_task = asyncio.create_task(redis_listener())
    print(">>> LIFESPAN: redis listener task created")

    try:
        print(">>> LIFESPAN: startup complete")
        yield
    finally:
        # ======================
        # SHUTDOWN
        # ======================
        print(">>> LIFESPAN: shutdown begin")

        redis_task.cancel()
        print(">>> LIFESPAN: redis listener cancelled")

        await disconnect_redis()
        print(">>> LIFESPAN: redis disconnected")


def create_app() -> FastAPI:
    print(">>> CREATE_APP: creating FastAPI app")

    app = FastAPI(
        title="Digital Signage Backend",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix="/api/v1")
    print(">>> CREATE_APP: routers mounted")

    return app


app = create_app()













