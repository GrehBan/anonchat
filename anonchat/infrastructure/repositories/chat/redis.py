import json
from datetime import datetime
from redis.asyncio import Redis

from anonchat.infrastructure.repositories.base.redis import RedisRepo
from anonchat.domain.chat.repo import IChatRepo
from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.infrastructure.cache import key_gen


class RedisChatRepo(RedisRepo, IChatRepo):
    async def add(self, chat: PrivateChat) -> PrivateChat:
        chat_id = await self.redis.incr(key_gen.CHAT_SEQ)
        chat.id = chat_id
        
        data = {
            "id": chat.id,
            "u1": chat.user1_id,
            "u2": chat.user2_id,
            "active": int(chat.is_active),
            "dt": chat.created_at.isoformat()
        }
        
        raw = json.dumps(data)

        async with self.redis.pipeline() as pipe:
            pipe.set(key_gen.chat_meta(chat_id), raw)
            
            pipe.set(key_gen.user_active_chat(chat.user1_id), chat_id)
            pipe.set(key_gen.user_active_chat(chat.user2_id), chat_id)
            
            pipe.xadd(key_gen.STREAM_CHATS, {"type": "CREATE", "data": raw})
            
            await pipe.execute()
            
        return chat

    async def get_by_id(self, chat_id: int) -> PrivateChat | None:
        raw = await self.redis.get(key_gen.chat_meta(chat_id))
        if not raw:
            return None
        
        data = json.loads(raw)
        return PrivateChat(
            id=data["id"],
            user1_id=data["u1"],
            user2_id=data["u2"],
            is_active=bool(data["active"]),
            created_at=datetime.fromisoformat(data["dt"])
        )

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
            
            pipe.expire(key_gen.chat_meta(chat_id), 3600)
            pipe.expire(key_gen.chat_messages_list(chat_id), 3600)

            event = {
                "type": "CLOSE", 
                "chat_id": str(chat_id), 
                "closed_at": datetime.utcnow().isoformat()
            }
            pipe.xadd(key_gen.STREAM_CHATS, event)
            
            await pipe.execute()
