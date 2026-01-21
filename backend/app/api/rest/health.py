from fastapi import APIRouter
from sqlalchemy import text

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.redis.client import redis

import time

router = APIRouter(tags=["health"])

START_TIME = time.time()


async def check_database() -> bool:
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def check_redis() -> bool:
    try:
        if redis is None:
            return False
        return await redis.ping()
    except Exception:
        return False


@router.get("/health")
async def health():
    db_ok = await check_database()
    redis_ok = await check_redis()

    status = "ok" if db_ok and redis_ok else "degraded"

    return {
        "status": status,
        "database": db_ok,
        "redis": redis_ok,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "1.0.0",
    }
