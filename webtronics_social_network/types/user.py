import uuid
import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from webtronics_social_network import dto
from webtronics_social_network.types.common import Update


class UserValidators(BaseModel):
    username: str = Field(min_length=4, max_length=24)
    password: str = Field(min_length=8, max_length=64)


class User(UserValidators):
    id: uuid.UUID

    created_at: dt.datetime

    @classmethod
    def from_dto(cls, user: dto.User) -> "User":
        return User(
            id=user.id,
            username=user.username,
            password=user.password,
            created_at=user.created_at
        )


class UserLogin(UserValidators):
    pass


class UserCreate(UserValidators):
    pass


class UserUpdate(UserValidators, Update):
    password: Optional[str] # type: ignore
