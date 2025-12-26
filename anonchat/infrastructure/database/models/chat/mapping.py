from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.infrastructure.database.models.user.mapping import map_user_model_to_entity

from anonchat.infrastructure.database.models.chat.chat import PrivateChatModel


def map_chat_model_to_entity(model: PrivateChatModel) -> PrivateChat:
    if model.user1 is None or model.user2 is None:
        raise ValueError(f"Chat {model.chat_id} loaded without user relations. Check eager loading.")

    user1_entity = map_user_model_to_entity(model.user1)
    user2_entity = map_user_model_to_entity(model.user2)

    return PrivateChat(
        id=model.chat_id,
        user1=user1_entity,
        user2=user2_entity,
        is_active=model.is_active,
        created_at=model.created_at
    )


def map_chat_entity_to_model_kwargs(entity: PrivateChat) -> dict:
    return {
        "id": entity.id if entity.id else None,
        "user1_id": entity.user1.id,
        "user2_id": entity.user2.id,
        "is_active": entity.is_active,
        "created_at": entity.created_at
    }
