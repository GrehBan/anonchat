from typing import Protocol

from anonchat.domain.chat.uow import IChatUoW
from anonchat.domain.chat.dto import StartChatRequestDTO, PrivateChatDTO
from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.domain.chat import mapping


class IStartChat(Protocol):
    uow: IChatUoW

    async def execute(self, initiator_id: int, dto: StartChatRequestDTO) -> PrivateChatDTO:
        ...


class StartChat(IStartChat):
    def __init__(self, uow: IChatUoW):
        self.uow = uow
    
    async def execute(self, initiator_id: int, dto: StartChatRequestDTO) -> PrivateChatDTO:
        if initiator_id == dto.user2_id:
             raise ValueError("Cannot start chat with yourself")

        async with self.uow:
            existing_chat = await self.uow.repo.get_chat_between(
                initiator_id, dto.user2_id
            )
            
            if existing_chat:
                return mapping.chat_to_dto(existing_chat)

            user1 = await self.uow.user_repo.get_by_id(initiator_id)
            user2 = await self.uow.user_repo.get_by_id(dto.user2_id)

            if not user1 or not user2:
                raise ValueError("One or both users not found")

            new_chat = PrivateChat(
                chat_id=0,
                user1=user1,
                user2=user2
            )

            new_chat_id = await self.uow.repo.add(new_chat)
            new_chat.id = new_chat_id

            await self.uow.commit()

            return mapping.chat_to_dto(new_chat)
