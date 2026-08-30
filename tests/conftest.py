import os
import subprocess
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import get_db

# Real Postgres required — the balance-enforcement trigger is Postgres-only
# and must actually be created by running migrations, not create_all().
DATABASE_URL_TEST = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://ledger_user:ledger_password@localhost:5432/ledgerflow_test",
)

# NullPool: forces a fresh connection every time instead of reusing a pooled
# connection across pytest-asyncio's per-test event loops, which caused
# "attached to a different loop" RuntimeErrors.
engine_test_instance = create_async_engine(
    DATABASE_URL_TEST, echo=False, future=True, poolclass=NullPool
)
async_session_test = async_sessionmaker(
    engine_test_instance, class_=AsyncSession, expire_on_commit=False
)


def _run_alembic_upgrade():
    subprocess.run(
        ["alembic", "upgrade", "head"],
        env={**os.environ, "DATABASE_URL": DATABASE_URL_TEST},
        check=True,
    )


def _run_alembic_downgrade():
    subprocess.run(
        ["alembic", "downgrade", "base"],
        env={**os.environ, "DATABASE_URL": DATABASE_URL_TEST},
        check=True,
    )


@pytest.fixture(autouse=True)
async def setup_database():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run_alembic_upgrade)
    yield
    await loop.run_in_executor(None, _run_alembic_downgrade)


@pytest.fixture(autouse=True)
async def reset_redis_client():
    """Disconnect the Redis client pool before/after tests to prevent event loop mismatch errors."""
    try:
        from app.db.redis import redis_client
        if redis_client:
            await redis_client.connection_pool.disconnect()
    except (ImportError, AttributeError):
        pass
    yield
    try:
        from app.db.redis import redis_client
        if redis_client:
            await redis_client.connection_pool.disconnect()
    except (ImportError, AttributeError):
        pass


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_test() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    # Each request gets its OWN session (not one shared session reused across
    # concurrent requests) — AsyncSession is not safe for concurrent use.
    async def override_get_db():
        async with async_session_test() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def engine_test():
    return engine_test_instance