from redis.asyncio import Redis

from anonchat.infrastructure.uow.base.redis import BaseRedisUoW
from anonchat.infrastructure.uow.user.redis import RedisUserUoW
from anonchat.infrastructure.uow.chat.redis import RedisChatUoW
from anonchat.infrastructure.uow.message.redis import RedisMessageUoW


class RedisUoW(BaseRedisUoW):
    def __init__(self, redis: Redis) -> None:
        super().__init__(redis)

        self.chat = RedisChatUoW(redis)
        self.user = RedisUserUoW(redis)
        self.message = RedisMessageUoW(redis)
