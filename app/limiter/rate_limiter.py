from fastapi import HTTPException, Request, status
from app.core.redis_client import get_redis


class RedisRateLimiter:
    def __init__(
        self,
        limit: int,
        window: int,
        key_prefix: str,
    ):
        self.limit = limit
        self.window = window
        self.key_prefix = key_prefix

    async def __call__(self, request: Request):
        redis = get_redis()

        client_ip = request.client.host if request.client else "unknown"

        key = f"rate_limit:{self.key_prefix}:{client_ip}"

        current = await redis.incr(key)

        if current == 1:
            await redis.expire(key, self.window)

        if current > self.limit:
            ttl = await redis.ttl(key)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Try again in {ttl} seconds.",
            )