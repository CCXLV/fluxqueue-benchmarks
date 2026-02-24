import multiprocessing
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

from benchmarks.config import SQLALCHEMY_DATABASE_URL

MAX_POOL_SIZE = 1000 // (multiprocessing.cpu_count() * 2)
MAX_OVERFLOW = MAX_POOL_SIZE // 2

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=MAX_POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


@asynccontextmanager
async def session_context():
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def get_session():
    async with session_context() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_session)]
