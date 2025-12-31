from redis.asyncio import Redis

from anonchat.domain.base.repo import IRepo


class RedisRepo(IRepo):
    DEFAULT_TTL: int | None = None

    def __init__(self, redis: Redis, ttl: int | None = None) -> None:
        self._redis = redis
        if ttl is None:
            ttl = self.DEFAULT_TTL
        self._ttl = ttl
    
    @property
    def redis(self) -> Redis:
        return self._redis

