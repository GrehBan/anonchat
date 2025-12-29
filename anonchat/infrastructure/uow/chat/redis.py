from redis.asyncio import Redis

from anonchat.domain.chat.uow import ILockChatUoW
from anonchat.infrastructure.uow.base.redis import BaseRedisUoW
from anonchat.infrastructure.repositories.chat.redis import RedisChatRepo
from anonchat.infrastructure.repositories.user.redis import RedisUserRepo
from anonchat.infrastructure.repositories.message.redis import RedisMessageRepo


class RedisChatUoW(BaseRedisUoW, ILockChatUoW):
    def __init__(self, redis: Redis) -> None:
        super().__init__(redis)

        self.repo = RedisChatRepo(redis)
        self.user_repo = RedisUserRepo(redis)
        self.message_repo = RedisMessageRepo(redis)
