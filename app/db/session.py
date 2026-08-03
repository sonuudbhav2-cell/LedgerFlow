from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase  # <--- Added this
from app.core.config import settings


# Base class for SQLAlchemy models
class Base(DeclarativeBase):  # <--- Added this
    pass


# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# FastAPI Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session