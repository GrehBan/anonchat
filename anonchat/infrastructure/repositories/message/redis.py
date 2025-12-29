import json
from datetime import datetime
from redis.asyncio import Redis

from anonchat.infrastructure.repositories.base.redis import RedisRepo
from anonchat.domain.message.repo import IMessageRepo
from anonchat.domain.message.aggregate import Message
from anonchat.domain.message.value_object import MessageContent, MessageText, MediaAttachment
from anonchat.infrastructure.cache import key_gen


class RedisMessageRepo(RedisRepo, IMessageRepo):
    def __init__(self, redis: Redis):
        super().__init__(redis=redis)
        self._ttl = 86400 * 3

    async def add(self, message: Message) -> Message:
        msg_id = await self.redis.incr(key_gen.MESSAGE_SEQ)
        message.id = msg_id
        
        media_ids = [m.file_id for m in message.content.media]
        
        data = {
            "id": msg_id,
            "cid": message.chat_id,
            "sid": message.sender_id,
            "txt": message.content.raw_text,
            "media": media_ids,
            "dt": message.created_at.isoformat()
        }
        raw_json = json.dumps(data)
        
        msg_key = key_gen.message_data(msg_id)
        timeline_key = key_gen.chat_messages_timeline(message.chat_id)

        async with self.redis.pipeline() as pipe:
            pipe.set(msg_key, raw_json, ex=self._ttl)
            
            pipe.rpush(timeline_key, msg_id)
            pipe.ltrim(timeline_key, -1000, -1)
            pipe.expire(timeline_key, self._ttl)
            
            stream_data = {
                "id": str(msg_id),
                "cid": str(message.chat_id),
                "sid": str(message.sender_id),
                "txt": message.content.raw_text or "",
                "media": json.dumps(media_ids),
                "dt": message.created_at.isoformat()
            }
            stream_data = {k: v for k, v in stream_data.items() if v}
            pipe.xadd(key_gen.STREAM_MESSAGES, stream_data)
            
            await pipe.execute()
            
        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        raw = await self.redis.get(key_gen.message_data(message_id))
        if not raw:
            return None
            
        data = json.loads(raw)
        return self._deserialize(data)

    async def delete(self, message_id: int) -> None:
        msg = await self.get_by_id(message_id)
        if not msg:
            return

        timeline_key = key_gen.chat_messages_timeline(msg.chat_id)
        msg_key = key_gen.message_data(message_id)

        async with self.redis.pipeline() as pipe:
            pipe.delete(msg_key)
            
            pipe.lrem(timeline_key, 0, message_id)

            pipe.xadd(key_gen.STREAM_MESSAGES_DELETE, {"id": str(message_id)})
            
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
                result.append(self._deserialize(data))
        
        return result

    def _deserialize(self, data: dict) -> Message:
        text_vo = MessageText(data["txt"]) if data.get("txt") else None
        media_vo = tuple(MediaAttachment(mid) for mid in data.get("media", []))
        
        return Message(
            id=data["id"],
            chat_id=data["cid"],
            sender_id=data["sid"],
            content=MessageContent(text=text_vo, media=media_vo),
            created_at=datetime.fromisoformat(data["dt"])
        )

    async def count_by_chat_id(self, chat_id: int) -> int:
        return await self.redis.llen(key_gen.chat_messages_timeline(chat_id))
