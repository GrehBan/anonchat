from redis.asyncio import Redis

from anonchat.domain.message.uow import ILockMessageUoW
from anonchat.infrastructure.uow.base.redis import BaseRedisUoW
from anonchat.infrastructure.repositories.message.redis import RedisMessageRepo


class RedisMessageUoW(BaseRedisUoW, ILockMessageUoW):
    def __init__(self, redis: Redis) -> None:
        super().__init__(redis)
        self.repo = RedisMessageRepo(redis)
