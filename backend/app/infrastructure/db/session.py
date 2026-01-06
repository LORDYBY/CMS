# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# from app.settings import settings

# engine = create_async_engine(
#     settings.DATABASE_URL,
#     echo=False,
#     pool_pre_ping=True
# )

# AsyncSessionLocal = async_sessionmaker(
#     engine,
#     expire_on_commit=False
# )

# async def get_session():
#     async with AsyncSessionLocal() as session:
#         yield session


from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from app.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

