from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from webtronics_social_network.server.api.api_v1.dependencies.database.postgres import PostgresEngineMarker
from webtronics_social_network.server.api.api_v1.dependencies.database.redis import RedisClientMarker


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    engine: AsyncEngine = app.dependency_overrides[PostgresEngineMarker]()
    redis: Redis = app.dependency_overrides[RedisClientMarker]()

    await engine.dispose()
    await redis.close()
