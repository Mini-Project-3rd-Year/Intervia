"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


settings = get_settings()


@lru_cache(maxsize=1)
def get_engine():
    return create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory():
    return async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)


engine = None
SessionLocal = None


async def get_db() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session