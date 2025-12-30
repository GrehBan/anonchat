from redis.asyncio import Redis
from anonchat.domain.base.lock import ILock, ILockFactory


class RedisLockFactory(ILockFactory):
    def __init__(self, client: Redis):
        self._client = client

    def lock(self, key: str, ttl_ms: int = 5000, blocking_timeout: int | float = 2.0) -> ILock:
        return self._client.lock(
            name=key, 
            timeout=ttl_ms / 1000.0,
            blocking_timeout=blocking_timeout
        )
    
    def __call__(self, key: str, ttl_ms: int = 5000) -> ILock:
        return self.lock(
            key, ttl_ms
        )
