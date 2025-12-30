import json
from datetime import datetime
from typing import Final

from anonchat.infrastructure.repositories.base.redis import RedisRepo
from anonchat.domain.message.repo import IMessageRepo
from anonchat.domain.message.aggregate import Message
from anonchat.infrastructure.cache import key_gen
from anonchat.infrastructure.repositories.message import mapping

TTL: Final[int] = 86400 * 3


class RedisMessageRepo(RedisRepo, IMessageRepo):
    DEFAULT_TTL: int | None = TTL

    async def add(self, message: Message) -> Message:
        msg_id: int = await self.redis.incr(key_gen.MESSAGE_SEQ)
        message.id = msg_id
                
        data, stream_data = mapping.map_message_entity_to_redis_data(message)

        raw_json = json.dumps(data)
        raw = json.dumps(stream_data)
        
        msg_key = key_gen.message_data(msg_id)
        timeline_key = key_gen.chat_messages_timeline(message.chat_id)

        async with self.redis.pipeline() as pipe:
            pipe.set(msg_key, raw_json, ex=self._ttl)
            
            pipe.rpush(timeline_key, msg_id)
            pipe.expire(timeline_key, self._ttl)

            stream_data = {k: v for k, v in stream_data.items() if v}
            pipe.xadd(key_gen.STREAM_MESSAGES, {"type": "SAVE", "raw": raw})
            
            await pipe.execute()
            
        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        raw = await self.redis.get(key_gen.message_data(message_id))
        if not raw:
            return None
            
        data = json.loads(raw)
        return mapping.map_redis_data_to_message_entity(data)

    async def delete(self, message_id: int) -> None:
        msg = await self.get_by_id(message_id)
        if not msg:
            return

        timeline_key = key_gen.chat_messages_timeline(msg.chat_id)
        msg_key = key_gen.message_data(message_id)

        async with self.redis.pipeline() as pipe:
            pipe.delete(msg_key)
            
            pipe.lrem(timeline_key, 0, message_id)

            pipe.xadd(key_gen.STREAM_MESSAGES, {"type": "DELETE", "id": str(message_id)})
            
            await pipe.execute()

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        timeline_key = key_gen.chat_messages_timeline(chat_id)
        
        start = -limit - offset
        end = -1 - offset
        
        msg_ids_raw = await self.redis.lrange(timeline_key, start, end)
        if not msg_ids_raw:
            return []
            
        msg_keys = [key_gen.message_data(int(mid)) for mid in msg_ids_raw]
        
        raw_messages = await self.redis.mget(msg_keys)
        
        result = []
        for raw in raw_messages:
            if raw:
                data = json.loads(raw)
                result.append(mapping.map_redis_data_to_message_entity(data))
        
        return result

    async def count_by_chat_id(self, chat_id: int) -> int:
        return await self.redis.llen(key_gen.chat_messages_timeline(chat_id))
