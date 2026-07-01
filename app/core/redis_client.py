import redis.asyncio as redis

from app.core.config import settings

redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis client has not been initialized.")
    return redis_client


async def init_redis() -> None:
    global redis_client

    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )


async def close_redis() -> None:
    global redis_client

    if redis_client is not None:
        await redis_client.aclose()   
        redis_client = None