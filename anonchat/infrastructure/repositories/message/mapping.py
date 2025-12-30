import datetime
import json
from typing import TypedDict, List, Tuple

from anonchat.domain.message.aggregate import Message
from anonchat.domain.message.value_object import (
    MessageText,
    MessageContent,
    MediaAttachment,
)


class MessageRedisData(TypedDict):
    id: int
    cid: int
    sid: int
    txt: str
    media: List[str]
    dt: str


class MessageRedisStreamData(TypedDict):
    id: str
    cid: str
    sid: str
    txt: str
    media: str
    dt: str


def map_message_entity_to_redis_data(
    message: Message,
) -> tuple[MessageRedisData, MessageRedisStreamData]:
    media = [m.file_id for m in message.content.media]
    dt = message.created_at.isoformat()

    redis_data: MessageRedisData = {
        "id": message.id,
        "cid": message.chat_id,
        "sid": message.sender_id,
        "txt": message.content.raw_text,
        "media": media,
        "dt": dt,
    }

    stream_data: MessageRedisStreamData = {
        "id": str(message.id),
        "cid": str(message.chat_id),
        "sid": str(message.sender_id),
        "txt": message.content.raw_text or "",
        "media": json.dumps(media),
        "dt": dt,
    }

    return redis_data, stream_data


def map_redis_data_to_message_entity(data: MessageRedisData) -> Message:
    text_vo = MessageText(data["txt"]) if data.get("txt") else None
    media_vo = tuple(MediaAttachment(mid) for mid in data.get("media", []))

    return Message(
        id=data["id"],
        chat_id=data["cid"],
        sender_id=data["sid"],
        content=MessageContent(
            text=text_vo,
            media=media_vo,
        ),
        created_at=datetime.datetime.fromisoformat(data["dt"]),
    )
