import datetime
from typing import TypedDict

from anonchat.domain.chat.aggregate import PrivateChat


class ChatRedisData(TypedDict):
    id: int
    u1: int
    u2: int
    active: int
    dt: str


def map_chat_entity_to_redis_data(chat: PrivateChat) -> ChatRedisData:
    data: ChatRedisData = {
        "id": chat.id,
        "u1": chat.user1_id,
        "u2": chat.user2_id,
        "active": int(chat.is_active),
        "dt": chat.created_at.isoformat(),
    }
    return data


def map_redis_data_to_chat_entity(data: ChatRedisData) -> PrivateChat:
    return PrivateChat(
        id=data["id"],
        user1_id=data["u1"],
        user2_id=data["u2"],
        is_active=bool(data["active"]),
        created_at=datetime.datetime.fromisoformat(data["dt"]),
    )
