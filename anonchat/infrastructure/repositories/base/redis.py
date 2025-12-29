from redis.asyncio import Redis

from anonchat.domain.base.repo import IRepo


class RedisRepo(IRepo):
    def __init__(self, redis: Redis):
        self._redis = redis
    
    @property
    def redis(self) -> Redis:
        return self._redis

