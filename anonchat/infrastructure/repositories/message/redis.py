from typing import Final

from anonchat.infrastructure.repositories.base.redis import RedisRepo
from anonchat.domain.message.repo import IMessageRepo
from anonchat.domain.message.aggregate import Message
from anonchat.infrastructure.cache import key_gen
from anonchat.infrastructure.repositories.message import mapping
from anonchat.infrastructure.cache.serialization import json

TTL: Final[int] = 86400 * 3


class RedisMessageRepo(RedisRepo, IMessageRepo):
    DEFAULT_TTL: int | None = TTL

    async def add(self, message: Message) -> Message:
        timeline_key = key_gen.chat_messages_timeline(message.chat_id)
        
        async with self.redis.pipeline() as pipe:
            pipe.incr(key_gen.MESSAGE_SEQ)
            pipe.llen(timeline_key)
            results = await pipe.execute()
            
            msg_id: int = results[0]
            sequence: int = results[1]
        
        message.id = msg_id
        message.sequence = sequence
                
        data, stream_data = mapping.map_message_entity_to_redis_data(message)

        raw_json = json.dumps(data)
        raw = json.dumps(stream_data)
        
        msg_key = key_gen.message_data(msg_id)

        async with self.redis.pipeline() as pipe:
            pipe.set(msg_key, raw_json, ex=self._ttl)
            pipe.rpush(timeline_key, msg_id)
            pipe.execute_command('EXPIRE', timeline_key, self._ttl, 'NX')
            pipe.xadd(key_gen.get_message_stream(message.id), {"type": "SAVE", "raw": raw})
            await pipe.execute()
            
        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        raw = await self.redis.get(key_gen.message_data(message_id))
        if not raw:
            return None
            
        data = json.loads(raw)
        message = mapping.map_redis_data_to_message_entity(data)
        
        return message

    async def delete(self, message_id: int) -> None:
        msg = await self.get_by_id(message_id)
        if not msg or msg.is_deleted:
            return
        
        msg.soft_delete()
        
        data, stream_data = mapping.map_message_entity_to_redis_data(msg)
        raw_json = json.dumps(data)
        raw = json.dumps(stream_data)
        
        msg_key = key_gen.message_data(message_id)

        async with self.redis.pipeline() as pipe:
            pipe.set(msg_key, raw_json, ex=self._ttl)
            pipe.xadd(
                key_gen.get_message_stream(message_id), 
                {"type": "SOFT_DELETE", "raw": raw}
            )
            
            await pipe.execute()

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:

        timeline_key = key_gen.chat_messages_timeline(chat_id)
        fetch_limit = int(limit * 1.2) + offset
        start = -fetch_limit
        end = -1 - offset if offset > 0 else -1
        
        msg_ids_raw = await self.redis.lrange(timeline_key, start, end)
        if not msg_ids_raw:
            return []
            
        msg_keys = [key_gen.message_data(int(mid)) for mid in msg_ids_raw]
        raw_messages = await self.redis.mget(msg_keys)
        
        result = []
        for raw in raw_messages:
            if raw:
                data = json.loads(raw)
                message = mapping.map_redis_data_to_message_entity(data)
                
                if not message.is_deleted:
                    result.append(message)
        
        result.sort(key=lambda m: m.sequence)
        
        return result[:limit]

    async def count_by_chat_id(self, chat_id: int) -> int:
        timeline_key = key_gen.chat_messages_timeline(chat_id)
        msg_ids = await self.redis.lrange(timeline_key, 0, -1)
        
        if not msg_ids:
            return 0
        
        msg_keys = [key_gen.message_data(int(mid)) for mid in msg_ids]
        raw_messages = await self.redis.mget(msg_keys)
        
        count = 0
        for raw in raw_messages:
            if raw:
                data = json.loads(raw)
                if not data.get("del_at"):
                    count += 1
        
        return count
    
    async def compact_timeline(self, chat_id: int) -> int:
        timeline_key = key_gen.chat_messages_timeline(chat_id)
        
        msg_ids = await self.redis.lrange(timeline_key, 0, -1)
        if not msg_ids:
            return 0
        
        msg_keys = [key_gen.message_data(int(mid)) for mid in msg_ids]
        raw_messages = await self.redis.mget(msg_keys)
        
        deleted_ids = []
        for mid, raw in zip(msg_ids, raw_messages):
            if raw:
                data = json.loads(raw)
                if data.get("del_at"):
                    deleted_ids.append(mid)
        
        if not deleted_ids:
            return 0
        
        async with self.redis.pipeline() as pipe:
            for mid in deleted_ids:
                pipe.lrem(timeline_key, 0, mid)
                pipe.delete(key_gen.message_data(int(mid)))
            
            await pipe.execute()
        
        return len(deleted_ids)