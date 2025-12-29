from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from anonchat.domain.base.lock import ILock, ILockFactory
from anonchat.infrastructure.cache import key_gen


class RedisLockFactory(ILockFactory):
    def __init__(self, client: Redis):
        self._client = client

    def lock(self, key: str, ttl_ms: int = 5000) -> ILock:
        return self._client.lock(
            name=key, 
            timeout=ttl_ms / 1000.0,
            blocking_timeout=2.0
        )
    
    def __call__(self, key: str, ttl_ms: int = 5000) -> ILock:
        return self.lock(
            key, ttl_ms
        )
