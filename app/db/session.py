from collections.abc import AsyncGenerator, Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

async_engine: AsyncEngine = create_async_engine(settings.async_database_url, echo=False)
sync_engine: Engine = create_engine(settings.sync_database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_db_sync() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
