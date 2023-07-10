from redis.asyncio.client import Redis

from webtronics_social_network.database.redis.holder import RedisHolder


def redis_create_client(connection_uri: str) -> Redis:
    return Redis.from_url(url=connection_uri)


def redis_create_holder(redis: Redis) -> RedisHolder:
    return RedisHolder(redis=redis)
