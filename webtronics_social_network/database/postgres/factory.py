from typing import AsyncGenerator, Callable, Any

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from webtronics_social_network.database.postgres.holder import PostgresHolder


def sa_create_engine(connection_uri: str, **engine_kwargs) -> AsyncEngine:
    return create_async_engine(url=connection_uri, **engine_kwargs)


def sa_create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


def sa_create_holder(session_factory: async_sessionmaker[AsyncSession]) -> Callable[[], AsyncGenerator[Any, Any]]:
    async def wrapper():
        async with session_factory() as session:
            yield PostgresHolder(session=session)

    return wrapper
