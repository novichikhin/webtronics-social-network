import uuid

from pydantic import BaseModel

from webtronics_social_network import dto, enums


class Reaction(BaseModel):
    id: uuid.UUID

    post_id: uuid.UUID
    user_id: uuid.UUID

    type: enums.ReactionType

    @classmethod
    def from_dto(cls, reaction: dto.Reaction) -> "Reaction":
        return Reaction(
            id=reaction.id,
            post_id=reaction.post_id,
            user_id=reaction.user_id,
            type=reaction.type
        )


class ReactionCreate(BaseModel):
    post_id: uuid.UUID
    type: enums.ReactionType
