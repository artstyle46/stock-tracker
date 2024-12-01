from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

from config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


class DB:
    def __init__(self):
        self.async_sessionmaker: sessionmaker | None = None

    async def __call__(self) -> AsyncIterator[AsyncSession]:
        """For use with FastAPI Depends"""
        if not self.async_sessionmaker:
            raise ValueError("async_sessionmaker not available. Run setup() first.")
        async with self.async_sessionmaker() as session:
            yield session

    def setup(self) -> None:
        self.async_engine = create_async_engine(settings.DATABASE_URL, echo=True)
        self.async_sessionmaker = sessionmaker(
            self.async_engine, class_=AsyncSession, expire_on_commit=False
        )

    async def close_db(self) -> None:
        await self.async_engine.dispose()


get_db = DB()
