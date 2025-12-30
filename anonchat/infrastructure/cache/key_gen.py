from typing import Final

NAMESPACE: Final[str] = "anochat"
MESSAGE_SEQ: Final[str] = f"{NAMESPACE}:global:message_id_seq"
CHAT_SEQ: Final[str] = f"{NAMESPACE}:global:chat_id_seq"
CHAT_MESSAGES_PATTERN: Final[str] = f"{NAMESPACE}:chat:*:timeline"
SHARDS_COUNT: Final[int] = 4

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

def get_user_stream(user_id: int) -> str:
    shard_id = user_id % SHARDS_COUNT
    return f"{NAMESPACE}:stream:users:{shard_id}"

def get_user_shard(shard_id: int) -> str:
    return f"{NAMESPACE}:stream:users:{shard_id}"

def get_user_shard_group(shard_id: int) -> str:
    return f"{NAMESPACE}:db-sync-users-shard-{shard_id}"

def get_chat_stream(chat_id: int) -> str:
    shard_id = chat_id % SHARDS_COUNT
    return f"{NAMESPACE}:stream:chats:{shard_id}"

def get_chat_shard(shard_id: int) -> str:
    return f"{NAMESPACE}:stream:chats:{shard_id}"

def get_chat_shard_group(shard_id: int) -> str:
    return f"{NAMESPACE}:db-sync-chats-shard-{shard_id}"

def get_message_stream(message_id: int) -> str:
    shard_id = message_id % SHARDS_COUNT
    return f"{NAMESPACE}:stream:messages:{shard_id}"

def get_message_shard(shard_id: int) -> str:
    return f"{NAMESPACE}:stream:messages:{shard_id}"

def get_message_shard_group(shard_id: int) -> str:
    return f"{NAMESPACE}:db-sync-messages-shard-{shard_id}"
