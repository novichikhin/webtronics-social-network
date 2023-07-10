import redis.asyncio as redis

from webtronics_social_network.database.redis.repositories.reaction import ReactionRepository


class RedisHolder:

    def __init__(self, redis: redis.Redis):
        self.reaction = ReactionRepository(redis=redis)
