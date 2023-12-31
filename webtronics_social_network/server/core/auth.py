import uuid

from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from jose.constants import ALGORITHMS
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from webtronics_social_network import types
from webtronics_social_network.server.api.api_v1.dependencies.database.postgres import PostgresHolderMarker
from webtronics_social_network.server.api.api_v1.dependencies.settings import SettingsMarker
from webtronics_social_network.server.core.security import verify_password
from webtronics_social_network.database.postgres.holder import PostgresHolder

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials"
)


def get_token(authorization: str) -> str:
    scheme, _, param = authorization.partition(" ")

    if scheme.lower() != "bearer":
        raise credentials_exception

    return param


async def verify_refresh_token(
        authorization: str = Header(alias="Authorization"),
        settings: types.Setting = Depends(SettingsMarker)
) -> types.RefreshToken:
    refresh_token = get_token(authorization=authorization)

    try:
        payload = jwt.decode(
            token=refresh_token,
            key=settings.authorize_refresh_token_secret_key,
            algorithms=[ALGORITHMS.HS256]
        )

        if not (user_id := payload.get("user_id")):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return types.RefreshToken(token=refresh_token, user_id=uuid.UUID(user_id))


async def authenticate_user(
        username: str,
        password: str,
        pg_holder: PostgresHolder,
        crypt_context: CryptContext
) -> types.User:
    user = await pg_holder.user.read_by_login(username=username)

    if not user or not verify_password(
            crypt_context=crypt_context,
            plain_password=password,
            hashed_password=user.password
    ):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Wrong username (email) or password"
        )

    return types.User.from_dto(user=user)


async def get_user(
        authorization: str = Header(alias="Authorization"),
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        settings: types.Setting = Depends(SettingsMarker)
) -> types.User:
    try:
        payload = jwt.decode(
            token=get_token(authorization=authorization),
            key=settings.authorize_access_token_secret_key,
            algorithms=[ALGORITHMS.HS256]
        )

        user_id = payload.get("user_id")

        if not user_id:
            raise credentials_exception

        try:
            user_id = uuid.UUID(hex=user_id)
        except ValueError:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await pg_holder.user.read_by_id(user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Authentication user not found"
        )

    return types.User.from_dto(user=user)
