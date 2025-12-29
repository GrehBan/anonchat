from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.infrastructure.database.models.chat.chat import PrivateChatModel


def map_chat_model_to_entity(model: PrivateChatModel) -> PrivateChat:
    return PrivateChat(
        id=model.chat_id,
        user1_id=model.user1_id,
        user2_id=model.user2_id,
        is_active=model.is_active,
        created_at=model.created_at
    )


def map_chat_entity_to_model(entity: PrivateChat) -> PrivateChatModel:
    return PrivateChatModel(
        user1_id=entity.user1_id,
        user2_id=entity.user2_id,
        is_active=entity.is_active,
        created_at=entity.created_at
    )