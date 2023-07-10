import datetime as dt
import uuid
from typing import Optional

from pydantic import BaseModel, Field

from webtronics_social_network import dto
from webtronics_social_network.types import Reaction
from webtronics_social_network.types.common import Update


class PostValidators(BaseModel):
    title: str = Field(min_length=10, max_length=64)
    body: str = Field(min_length=10, max_length=256)


class Post(PostValidators):
    id: uuid.UUID

    created_at: dt.datetime
    creator_id: uuid.UUID

    reactions: list["Reaction"] = Field(default_factory=list)

    @classmethod
    def from_dto(
            cls,
            post: dto.Post,
            reactions: Optional[list[dto.Reaction]] = None
    ) -> "Post":
        if not reactions:
            reactions = []
        else:
            reactions = [Reaction.from_dto(reaction=reaction) for reaction in reactions]

        return Post(
            id=post.id,
            title=post.title,
            body=post.body,
            created_at=post.created_at,
            creator_id=post.creator_id,
            reactions=reactions
        )


class PostCreate(PostValidators):
    pass


class PostUpdate(PostValidators, Update):
    title: Optional[str] # type: ignore
    body: Optional[str] # type: ignore
