import datetime
from typing import TypedDict, List

from anonchat.domain.message.aggregate import Message
from anonchat.domain.message.value_object import (
    MessageText,
    MessageContent,
    MediaAttachment,
)
from anonchat.infrastructure.cache.serialization import json


class MessageRedisData(TypedDict):
    id: int
    cid: int
    sid: int
    seq: int
    txt: str
    media: List[str]
    dt: str
    del_at: str | None


class MessageRedisStreamData(TypedDict):
    id: str
    cid: str
    sid: str
    seq: str
    txt: str
    media: str
    dt: str
    del_at: str


def map_message_entity_to_redis_data(
    message: Message,
) -> tuple[MessageRedisData, MessageRedisStreamData]:
    media = [m.file_id for m in message.content.media]
    dt = message.created_at.isoformat()
    del_at = message.deleted_at.isoformat() if message.deleted_at else None

    redis_data: MessageRedisData = {
        "id": message.id,
        "cid": message.chat_id,
        "sid": message.sender_id,
        "seq": message.sequence,
        "txt": message.content.raw_text,
        "media": media,
        "dt": dt,
        "del_at": del_at,
    }

    stream_data: MessageRedisStreamData = {
        "id": str(message.id),
        "cid": str(message.chat_id),
        "sid": str(message.sender_id),
        "seq": str(message.sequence),
        "txt": message.content.raw_text or "",
        "media": json.dumps(media),
        "dt": dt,
        "del_at": del_at or "",
    }

    return redis_data, stream_data


def map_redis_data_to_message_entity(data: MessageRedisData) -> Message:
    text_vo = MessageText(data["txt"]) if data.get("txt") else None
    media_vo = tuple(MediaAttachment(mid) for mid in data.get("media", []))
    
    deleted_at = None
    if data.get("del_at"):
        deleted_at = datetime.datetime.fromisoformat(data["del_at"])

    return Message(
        id=data["id"],
        chat_id=data["cid"],
        sender_id=data["sid"],
        sequence=data.get("seq", 0),
        content=MessageContent(
            text=text_vo,
            media=media_vo,
        ),
        created_at=datetime.datetime.fromisoformat(data["dt"]),
        deleted_at=deleted_at,
    )