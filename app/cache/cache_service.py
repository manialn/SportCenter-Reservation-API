import json
from typing import Any
from app.core.config import settings
from app.core.redis_client import get_redis


class CacheService:

    @property
    def redis(self):
        return get_redis()

    async def get(
        self,
        key: str,
    ) -> Any | None:
        data = await self.redis.get(key)

        if data is None:
            return None

        return json.loads(data)

    async def set(
        self,
        key: str,
        value: Any,
        expire: int | None = None,
    ) -> None:

        if expire is None:
            expire = settings.CACHE_EXPIRE_SECONDS

        await self.redis.set(
            key,
            json.dumps(value),
            ex=expire,
        )

    async def delete(
        self,
        key: str,
    ) -> None:
        await self.redis.delete(key)

    async def delete_pattern(
        self,
        pattern: str,
    ) -> None:
        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)

    async def exists(
        self,
        key: str,
    ) -> bool:
        return bool(await self.redis.exists(key))


cache_service = CacheService()