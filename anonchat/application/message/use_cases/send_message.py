from typing import Protocol

from anonchat.domain.chat.uow import IChatUoW
from anonchat.domain.message.dto import SendMessageDTO, MessageDTO
from anonchat.domain.message.aggregate import Message
from anonchat.domain.message import mapping
from anonchat.domain.chat.exceptions import ChatNotFoundException, ChatClosedException
from anonchat.domain.base.exceptions import PermissionDeniedException


class ISendMessage(Protocol):
    uow: IChatUoW

    async def execute(self, sender_id: int, chat_id: int, dto: SendMessageDTO) -> MessageDTO:
        ...


class SendMessage(ISendMessage):
    def __init__(self, uow: IChatUoW):
        self.uow = uow
    
    async def execute(self, sender_id: int, chat_id: int, dto: SendMessageDTO) -> MessageDTO:
        async with self.uow:
            chat = await self.uow.repo.get_by_id(chat_id)
            if not chat:
                raise ChatNotFoundException(f"Chat {chat_id} not found")
            
            if sender_id not in (chat.user1_id, chat.user2_id):
                 raise PermissionDeniedException("User is not a participant of this chat")
            
            if not chat.is_active:
                raise ChatClosedException("Chat is closed")

            content_vo = mapping.dto_to_message_content(dto)

            new_message = Message(
                id=0,
                chat_id=chat_id,
                sender_id=sender_id,
                content=content_vo
            )

            new_message = await self.uow.message_repo.add(new_message)

            await self.uow.commit()
            
            return mapping.message_to_dto(new_message)