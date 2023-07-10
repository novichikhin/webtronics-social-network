from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from passlib.context import CryptContext
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

from webtronics_social_network.server.api.api_v1.dependencies.database.postgres import (
    PostgresEngineMarker,
    PostgresSessionMarker,
    PostgresHolderMarker
)
from webtronics_social_network.server.api.api_v1.dependencies.database.redis import RedisClientMarker, RedisHolderMarker
from webtronics_social_network.database.redis.factory import redis_create_client, redis_create_holder
from webtronics_social_network.types import errors
from webtronics_social_network.server.api.api_v1.dependencies.security import CryptContextMarker
from webtronics_social_network.server.api.api_v1.dependencies.settings import SettingsMarker
from webtronics_social_network.server.api.api_v1.endpoints.setup import register_routers
from webtronics_social_network import types
from webtronics_social_network.database.postgres.factory import (
    sa_create_engine,
    sa_create_session_factory,
    sa_create_holder
)
from webtronics_social_network.server.core.event import lifespan
from webtronics_social_network.server.core.exceptions.handler import (
    http_exception_handler,
    request_validation_error_handler,
    exception_handler
)


def register_app(settings: types.Setting) -> FastAPI:
    app = FastAPI(
        exception_handlers={
            HTTPException: http_exception_handler,
            RequestValidationError: request_validation_error_handler,
            Exception: exception_handler
        },
        responses={
            HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error", "model": errors.Validation},
            HTTP_500_INTERNAL_SERVER_ERROR: {
                "description": "Something went wrong error",
                "model": errors.SomethingWentWrong
            }
        },
        lifespan=lifespan
    )

    crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    engine = sa_create_engine(connection_uri=settings.database_uri)
    session_factory = sa_create_session_factory(engine=engine)

    redis = redis_create_client(connection_uri=settings.redis_uri)

    app.include_router(router=register_routers(), prefix=settings.api_v1_str)

    app.dependency_overrides.update(
        {
            SettingsMarker: lambda: settings,
            PostgresEngineMarker: lambda: engine,
            PostgresSessionMarker: lambda: session_factory,
            PostgresHolderMarker: sa_create_holder(session_factory=session_factory),
            RedisClientMarker: lambda: redis,
            RedisHolderMarker: lambda: redis_create_holder(redis=redis),
            CryptContextMarker: lambda: crypt_context
        }
    )

    return app
