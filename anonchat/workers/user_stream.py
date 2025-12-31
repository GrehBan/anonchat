import asyncio
import json
import logging

from redis.asyncio import Redis
from redis import exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from anonchat.infrastructure.cache.worker import RedisWorker
from anonchat.infrastructure.cache import key_gen
from anonchat.infrastructure.repositories.user import mapping
from anonchat.infrastructure.repositories.user.sqlalchemy import SqlalchemyUserRepo

logger = logging.getLogger(__name__)


class UserStreamWorker(RedisWorker):
    def __init__(self, redis: Redis, session_maker: sessionmaker[AsyncSession], shard_id: int) -> None:
        stream_key = key_gen.get_user_shard(shard_id)
        group_name = key_gen.get_user_shard_group(shard_id)
        super().__init__(redis, group_name=group_name, stream_key=stream_key, shard_id=shard_id)

        self._session_maker = session_maker

    async def consume(self) -> None:
        await self.ensure_consumer_group(
            self._stream_key,
        )
        self._running = True
        logger.info(
            f"Worker {self.__class__.__name__} "
            f"SHARD-{self._shard_id}-{self._id} "
            f"started. Listening: {self._stream_key}"
        )

        while self._running:
            try:
                events = await self.redis.xreadgroup(
                    groupname=self._group_name,
                    consumername=f"worker-shard-{self._shard_id}-{self._id}",
                    streams={self._stream_key: ">"},
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

        async with self._session_maker() as session:
            repo = SqlalchemyUserRepo(session)

            data_type = self._get_data_and_decode(data, "type")

            if data_type in ("SAVE", "UPDATE",):

                raw = self._get_data_and_decode(data, "raw")
                user_data = self._load(raw)
                
                if user_data is None:
                    return
                user = mapping.map_redis_data_to_user_entity(user_data)

                if data_type == "UPDATE":
                    await repo.update(user)
                else:
                    if (await repo.get_by_id(user.id)):
                        return
                    await repo.add(user)

            elif data_type == "DELETE":
                _id = self._get_data_and_decode(data, "id")
                await repo.delete_by_id(int(_id))
            
            await session.commit()
