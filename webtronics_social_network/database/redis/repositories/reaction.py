import uuid

import msgpack
import redis.asyncio as redis

from webtronics_social_network import dto, enums
from webtronics_social_network.database.redis import models
from webtronics_social_network.database.redis.models.reaction import REACTION_KEY_MASK
from webtronics_social_network.database.redis.repositories.main import RedisRepository


class ReactionRepository(RedisRepository[models.Reaction]):

    def __init__(self, redis: redis.Redis):
        super().__init__(model=models.Reaction, redis=redis)

    async def create(
            self,
            reaction_id: uuid.UUID,
            post_id: uuid.UUID,
            user_id: uuid.UUID,
            type: enums.ReactionType
    ) -> dto.Reaction:
        reaction = models.Reaction(
            id=reaction_id,
            post_id=post_id,
            user_id=user_id,
            type=type
        )

        await self._redis.set(
            name=reaction.key,
            value=msgpack.packb(
                dict(
                    id=str(reaction.id),
                    post_id=str(reaction.post_id),
                    user_id=str(reaction.user_id),
                    type=str(reaction.type.value)
                )
            )
        )

        return reaction.to_dto()

    async def read_by_post_id(self, post_id: uuid.UUID) -> list[dto.Reaction]:
        reactions: list[dto.Reaction] = []

        reaction_keys = await self._redis.keys(REACTION_KEY_MASK.format(reaction_id="*", post_id=post_id, user_id="*"))

        for reaction_key in reaction_keys:
            reaction = msgpack.unpackb(await self._redis.get(reaction_key))

            reaction = dto.Reaction(
                id=uuid.UUID(reaction["id"]),
                post_id=post_id,
                user_id=uuid.UUID(reaction["user_id"]),
                type=enums.ReactionType(reaction["type"])
            )

            reactions.append(reaction)

        return reactions

    async def delete(
            self,
            reaction_id: uuid.UUID,
            post_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        key = REACTION_KEY_MASK.format(
            reaction_id=reaction_id,
            post_id=post_id,
            user_id=user_id
        )

        deleted = await self._redis.delete(key)
        return bool(deleted)

    async def delete_by_post_id(self, post_id: uuid.UUID) -> bool:
        reactions = await self.read_by_post_id(post_id=post_id)

        async with self._redis.pipeline(transaction=True) as pipe:
            for reaction in reactions:
                reaction = models.Reaction(
                    id=reaction.id,
                    post_id=reaction.post_id,
                    user_id=reaction.user_id,
                    type=reaction.type
                )

                pipe.delete(reaction.key)

            await pipe.execute()

        return True
