from redis.asyncio import Redis

from anonchat.domain.base.uow import ILockUoW
from anonchat.infrastructure.cache.redis_lock import RedisLockFactory


class BaseRedisUoW(ILockUoW):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis
        self.lock = RedisLockFactory(redis)

    @property
    def redis(self) -> Redis:
        return self._redis

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def __aenter__(self) -> "BaseRedisUoW":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    async def close(self):
        await self.redis.close()