from redis.asyncio import Redis

from anonchat.domain.user.uow import ILockUserUoW
from anonchat.infrastructure.uow.base.redis import BaseRedisUoW
from anonchat.infrastructure.repositories.user.redis import RedisUserRepo


class RedisUserUoW(BaseRedisUoW, ILockUserUoW):
    def __init__(self, redis: Redis) -> None:
        super().__init__(redis)
        self.repo = RedisUserRepo(redis)
