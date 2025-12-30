import asyncio
import json
import logging

from redis.asyncio import Redis
from redis import exceptions

from anonchat.domain.chat.repo import IChatRepo
from anonchat.infrastructure.cache.worker import RedisWorker
from anonchat.infrastructure.cache import key_gen
from anonchat.infrastructure.repositories.chat import mapping

logger = logging.getLogger(__name__)


class ChatStreamWorker(RedisWorker):
    def __init__(self, redis: Redis, repo: IChatRepo) -> None:
        super().__init__(redis, group_name="chat-group")

        self.repo = repo

    async def consume(self) -> None:
        await self.ensure_consumer_group(
            key_gen.STREAM_CHATS,
        )
        self._running = True
        logger.info(f"{self.__class__.__name__} Started")

        while self._running:
            try:
                events = await self.redis.xreadgroup(
                    groupname=self._group_name,
                    consumername=f"worker-{self._id}",
                    streams={key_gen.STREAM_CHATS: ">"},
                    count=100,
                    block=1000
                )
                
                for stream, messages in events:
                    for msg_id, data in messages:
                        await self.process_with_retry(stream, msg_id, data)

            except (ConnectionError, exceptions.ConnectionError) as e:
                logger.error(f"Redis connection lost: {e}")
                await asyncio.sleep(5)
            
            except Exception as e:
                logger.error(f"Consumer error: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def process_event(self, data: dict):

        if data["type"] == "CREATE":
            chat_data = json.loads(data["data"])
            chat = mapping.map_redis_data_to_chat_entity(chat_data)
            await self.repo.add(chat)

        elif data["type"] == "CLOSE":
            chat = await self.repo.get_by_id(chat_id=int(data["id"]))
            if chat is not None:
                chat.is_active = False
                await self.repo.update(chat)
