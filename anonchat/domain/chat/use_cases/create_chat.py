from typing import Protocol

from anonchat.domain.chat.uow import IChatUoW
from anonchat.domain.chat.dto import StartChatRequestDTO, PrivateChatDTO
from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.domain.chat import mapping
from anonchat.domain.user import mapping as user_mapping


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
            user1 = await self.uow.user_repo.get_by_id(initiator_id)
            user2 = await self.uow.user_repo.get_by_id(dto.user2_id)

            if not user1 or not user2:
                raise ValueError("One or both users not found")

            user1_dto = user_mapping.user_to_profile_dto(user1)
            user2_dto = user_mapping.user_to_profile_dto(user2)

            existing_chat = await self.uow.repo.get_chat_between(
                initiator_id, dto.user2_id
            )
            
            if existing_chat:
                return mapping.chat_to_dto(existing_chat, user1_dto, user2_dto)

            new_chat = PrivateChat(
                id=0,
                user1_id=user1.id,
                user2_id=user2.id
            )

            new_chat_id = await self.uow.repo.add(new_chat)
            new_chat.id = new_chat_id

            await self.uow.commit()

            return mapping.chat_to_dto(new_chat, user1_dto, user2_dto)