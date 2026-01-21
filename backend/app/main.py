from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.logging import setup_logging
from app.infrastructure.redis.client import connect_redis, disconnect_redis
from app.infrastructure.redis.subscriber import redis_listener

from app.api.rest import router as api_router
from app.api.rest.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
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
        print(">>> LIFESPAN: shutdown begin")

        redis_task.cancel()
        try:
            await redis_task
        except asyncio.CancelledError:
            pass

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



    # Mount API routers
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(health_router)  # <---- CORRECT HEALTH ROUTER

    print("\n=== REGISTERED ROUTES ===")
    for r in app.routes:
        print("•", r.path, "→", r.name)
    print("=========================\n")

    print(">>> CREATE_APP: routers mounted")
    return app




app = create_app()
