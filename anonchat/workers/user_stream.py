import asyncio

from redis.asyncio import Redis
from redis import exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from anonchat.infrastructure.cache.worker import RedisWorker
from anonchat.infrastructure.cache import key_gen
from anonchat.application.user.handlers.redis import ProcessRedisUserEvent
from anonchat.infrastructure.uow.user.sqlalchemy import SqlalchemyUserUoW


class UserStreamWorker(RedisWorker):
    def __init__(self, redis: Redis, session_maker: sessionmaker[AsyncSession], shard_id: int) -> None:
        stream_key = key_gen.get_user_shard(shard_id)
        group_name = key_gen.get_user_shard_group(shard_id)
        super().__init__(redis, group_name=group_name, stream_key=stream_key, shard_id=shard_id)

        self._session_maker = session_maker

    async def consume(self) -> None:
        await self.ensure_consumer_group(self._stream_key)
        
        self._running = True
        self._logger.info(
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
                
                if not events:
                    continue
                
                async with self._session_maker() as session:
                    handler = ProcessRedisUserEvent()
                    
                    for stream, messages in events:
                        for msg_id, data in messages:
                            try:
                                async with SqlalchemyUserUoW(session) as uow:
                                    await handler.handle(data, uow)
                                    await uow.commit()
                            except Exception as e:
                                self._logger.error(f"Error processing user event {msg_id}", e, exc_info=True)
                            else:
                                await self.redis.xack(stream, self._group_name, msg_id)

            except (ConnectionError, exceptions.ConnectionError) as e:
                self._logger.error(f"Redis connection lost: {e}")
                await asyncio.sleep(5)
            
            except Exception as e:
                self._logger.error(f"Consumer error: {e}", exc_info=True)
                await asyncio.sleep(1)