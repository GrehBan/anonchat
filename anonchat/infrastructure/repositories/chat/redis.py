import json
from datetime import datetime
from typing import Final

from anonchat.infrastructure.repositories.base.redis import RedisRepo
from anonchat.domain.chat.repo import IChatRepo
from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.infrastructure.cache import key_gen
from anonchat.infrastructure.repositories.chat import mapping

TTL: Final[int] = 86400 * 7


class RedisChatRepo(RedisRepo, IChatRepo):
    DEFAULT_TTL: int | None = TTL


    async def add(self, chat: PrivateChat) -> PrivateChat:

        async with self.redis.pipeline() as pipe:

            chat_id = await pipe.incr(key_gen.CHAT_SEQ)
            chat.id = chat_id
            stream_key = key_gen.get_chat_stream(chat.id)
        
            data = mapping.map_chat_entity_to_redis_data(chat)
            
            raw = json.dumps(data)

            pipe.set(key_gen.chat_meta(chat_id), raw)
            
            pipe.set(key_gen.user_active_chat(chat.user1_id), chat_id, ex=self._ttl)
            pipe.set(key_gen.user_active_chat(chat.user2_id), chat_id, ex=self._ttl)
            
            pipe.xadd(stream_key, {"type": "CREATE", "raw": raw})
            
            await pipe.execute()
            
        return chat

    async def get_by_id(self, chat_id: int) -> PrivateChat | None:
        raw = await self.redis.get(key_gen.chat_meta(chat_id))
        if not raw:
            return None
        
        data = json.loads(raw)
        return mapping.map_redis_data_to_chat_entity(data)

    async def get_active_chat_for_user(self, user_id: int) -> PrivateChat | None:
        chat_id = await self.redis.get(key_gen.user_active_chat(user_id))
        if not chat_id:
            return None
        
        return await self.get_by_id(int(chat_id))

    async def get_chat_between(self, user_id_1: int, user_id_2: int) -> PrivateChat | None:
        chat = await self.get_active_chat_for_user(user_id_1)
        if chat:
            if chat.user1_id == user_id_2 or chat.user2_id == user_id_2:
                return chat
        return None

    async def delete_chat(self, chat_id: int) -> None:
        chat = await self.get_by_id(chat_id)
        if not chat:
            return

        async with self.redis.pipeline() as pipe:
            pipe.delete(key_gen.user_active_chat(chat.user1_id))
            pipe.delete(key_gen.user_active_chat(chat.user2_id))
            
            pipe.expire(key_gen.chat_meta(chat_id))
            pipe.expire(key_gen.chat_messages_list(chat_id))

            event = {
                "type": "CLOSE", 
                "id": str(chat_id), 
                "closed_at": datetime.utcnow().isoformat()
            }
            pipe.xadd(key_gen.get_chat_stream(chat_id), event)
            
            await pipe.execute()
