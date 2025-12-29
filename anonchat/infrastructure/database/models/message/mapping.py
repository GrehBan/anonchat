from anonchat.domain.message.aggregate import Message
from anonchat.domain.message.value_object import MessageContent, MessageText, MediaAttachment
from anonchat.infrastructure.database.models.message.message import MessageModel


def map_message_model_to_entity(model: MessageModel) -> Message:
    text_vo = MessageText(model.content_text) if model.content_text else None
    
    media_data = model.content_media or []
    media_vo = tuple(MediaAttachment(file_id=fid) for fid in media_data)
    
    content_vo = MessageContent(text=text_vo, media=media_vo)

    return Message(
        id=model.message_id,
        chat_id=model.chat_id,
        sender_id=model.sender_id,
        content=content_vo,
        created_at=model.created_at
    )


def map_message_entity_to_model(entity: Message) -> MessageModel:
    text_val = entity.content.text.value if entity.content.text else None
    media_val = [m.file_id for m in entity.content.media]

    return MessageModel(
        chat_id=entity.chat_id,
        sender_id=entity.sender_id,
        content_text=text_val,
        content_media=media_val,
        created_at=entity.created_at
    )
