from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 1. Create Async Database Engine using asyncpg driver
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),  # Logs raw SQL queries during dev
    future=True,
    pool_size=10,       # Pre-warmed connection pool
    max_overflow=20,    # Extra temporary connections under heavy load
)

# 2. Factory that spawns isolated database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 3. Parent class for all our SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass

# 4. Dependency function that FastAPI calls on every API request
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()