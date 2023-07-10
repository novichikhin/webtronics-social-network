import uuid
from dataclasses import dataclass

from webtronics_social_network import enums, dto
from webtronics_social_network.database.redis.models.main import RedisBase

REACTION_KEY_MASK = "post_id:{post_id}:user_id:{user_id}"


@dataclass
class Reaction(RedisBase):
    post_id: uuid.UUID
    user_id: uuid.UUID
    type: enums.ReactionType

    @property
    def key(self) -> str:
        return REACTION_KEY_MASK.format(post_id=self.post_id, user_id=self.user_id)

    def to_dto(self) -> dto.Reaction:
        return dto.Reaction(
            post_id=self.post_id,
            user_id=self.user_id,
            type=self.type
        )
