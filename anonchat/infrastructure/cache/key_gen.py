from typing import Final

NAMESPACE: Final[str] = "anochat"
MESSAGE_SEQ: Final[str] = "global:message_id_seq"
CHAT_SEQ: Final[str] = "global:chat_id_seq"

STREAM_USERS: Final[str] = "stream:users_lifecycle"
STREAM_CHATS: Final[str] = "stream:chats_lifecycle"
STREAM_MESSAGES: Final[str] = "stream:messages_to_db"


def lock_user(user_id: int) -> str:
    return f"{NAMESPACE}:lock:user:{user_id}"

def user_data(user_id: int) -> str:
    return f"{NAMESPACE}:user:{user_id}:data"

def chat_meta(chat_id: int) -> str:
    return f"{NAMESPACE}:chat:{chat_id}:meta"

def user_active_chat(user_id: int) -> str:
    return f"{NAMESPACE}:user:{user_id}:chat"

def chat_messages_list(chat_id: int) -> str:
    return f"{NAMESPACE}:chat:{chat_id}:messages"

def message_data(message_id: int) -> str:
    return f"{NAMESPACE}:message:{message_id}:data"

def chat_messages_timeline(chat_id: int) -> str:
    return f"{NAMESPACE}:chat:{chat_id}:timeline"