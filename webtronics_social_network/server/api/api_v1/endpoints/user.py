import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_401_UNAUTHORIZED
)

from webtronics_social_network import types, exceptions
from webtronics_social_network.database.postgres.holder import PostgresHolder
from webtronics_social_network.services.auth import create_access_token, create_refresh_token
from webtronics_social_network.server.api.api_v1 import responses
from webtronics_social_network.server.api.api_v1.dependencies.database.postgres import PostgresHolderMarker
from webtronics_social_network.server.api.api_v1.dependencies.security import CryptContextMarker
from webtronics_social_network.server.api.api_v1.dependencies.settings import SettingsMarker
from webtronics_social_network.server.api.api_v1.responses.main import user_auth_responses
from webtronics_social_network.server.core.auth import (
    authenticate_user,
    get_user,
    verify_refresh_token
)
from webtronics_social_network.server.core.security import get_password_hash

router = APIRouter()


@router.post(
    "/login",
    response_model=types.Authentication,
    responses={
        HTTP_401_UNAUTHORIZED: {
            "description": "Wrong username (email) or password error",
            "model": responses.WrongUsernameOrPassword
        }
    }
)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        crypt_context: CryptContext = Depends(CryptContextMarker),
        settings: types.Setting = Depends(SettingsMarker)
):
    user: types.User = await authenticate_user(
        username=form_data.username,
        password=form_data.password,
        pg_holder=pg_holder,
        crypt_context=crypt_context
    )

    payload = {
        "user_id": str(user.id)
    }

    access_token = create_access_token(
        payload=payload,
        secret_key=settings.authorize_access_token_secret_key,
        expire_minutes=settings.authorize_access_token_expire_minutes
    )

    refresh_token = create_refresh_token(
        payload=payload,
        secret_key=settings.authorize_refresh_token_secret_key,
        expire_minutes=settings.authorize_refresh_token_expire_minutes
    )

    return types.Authentication(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post(
    "/refresh",
    response_model=types.AccessToken,
    responses={
        HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials error",
            "model": responses.NotValidateCredentials
        }
    }
)
async def refresh(
        refresh_token: types.RefreshToken = Depends(verify_refresh_token),
        settings: types.Setting = Depends(SettingsMarker)
):
    new_access_token = create_access_token(
        payload={"user_id": str(refresh_token.user_id)},
        secret_key=settings.authorize_access_token_secret_key,
        expire_minutes=settings.authorize_access_token_expire_minutes
    )

    return types.AccessToken(access_token=new_access_token, token_type="bearer")


@router.get(
    "/",
    response_model=list[types.User],
    dependencies=[Depends(get_user)],
    response_model_exclude={"email", "email_token", "email_verified", "password"},
    responses=user_auth_responses
)
async def read_all(
        offset: int = Query(default=0, ge=0, le=500),
        limit: int = Query(default=5, ge=1, le=1000),
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker)
):
    users = await pg_holder.user.read_all(offset=offset, limit=limit)

    return [types.User.from_dto(user=user) for user in users]


@router.get(
    "/{id}",
    response_model=types.User,
    dependencies=[Depends(get_user)],
    response_model_exclude={"email", "email_token", "email_verified", "password"},
    responses=user_auth_responses | {
        HTTP_404_NOT_FOUND: {
            "model": user_auth_responses[HTTP_404_NOT_FOUND]["model"] | responses.UserNotFound
        }
    }
)
async def read(id: uuid.UUID, pg_holder: PostgresHolder = Depends(PostgresHolderMarker)):
    user = await pg_holder.user.read_by_id(user_id=id)

    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return types.User.from_dto(user=user)


@router.post(
    "/",
    response_model=types.User,
    response_model_exclude={"password", "email_token"},
    responses={
        HTTP_409_CONFLICT: {
            "description": "User username already exists error",
            "model": responses.UsernameAlreadyExists
        }
    }
)
async def create(
        user_create: types.UserCreate,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        crypt_context: CryptContext = Depends(CryptContextMarker)
):
    try:
        user = await pg_holder.user.create(
            username=user_create.username,
            password=get_password_hash(crypt_context=crypt_context, password=user_create.password)
        )
    except exceptions.UsernameAlreadyExists:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="User username already exists"
        )

    return types.User.from_dto(user=user)
