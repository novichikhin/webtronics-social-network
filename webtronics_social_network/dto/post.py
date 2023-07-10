import uuid
import datetime as dt

from dataclasses import dataclass


@dataclass
class Post:
    id: uuid.UUID

    title: str
    body: str

    created_at: dt.datetime
    creator_id: uuid.UUID
