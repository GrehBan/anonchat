from anonchat.domain.message.dto import MessageDTO, SendMessageDTO
from anonchat.domain.message.value_object import MessageContent, MessageText, MediaAttachment
from anonchat.domain.message.aggregate import Message


def message_to_dto(message: Message) -> MessageDTO:
    media_list = [m.file_id for m in message.content.media] if message.content.has_media else []

    return MessageDTO(
        id=message.id,  # Fixed
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        text=message.content.raw_text,
        created_at=message.created_at,
        media=media_list
    )

def dto_to_message_content(dto: SendMessageDTO) -> MessageContent:
    text_vo = MessageText(dto.text) if dto.text else None
    media_vo = tuple(MediaAttachment(file_id=mid) for mid in (dto.media or []))

    return MessageContent(
        text=text_vo,
        media=media_vo
    )