import uuid

import redis.asyncio as redis

from abc import ABC
from typing import TypeVar, Generic, Union, Type

from webtronics_social_network.database.redis.models.main import RedisBase

Model = TypeVar("Model", bound=RedisBase)
Id = Union[int, uuid.UUID]


class RedisRepository(ABC, Generic[Model]):

    def __init__(self, model: Type[Model], redis: redis.Redis):
        self._model = model
        self._redis = redis
