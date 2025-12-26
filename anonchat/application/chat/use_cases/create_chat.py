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
        target_id = dto.user2_id
        
        if initiator_id == target_id:
            raise ValueError("Cannot start chat with yourself")

        async with self.uow:
            chat = await self.uow.repo.get_active_chat_for_user(initiator_id)

            if chat:
                if target_id not in (chat.user1_id, chat.user2_id):
                    raise ValueError("You already have an active chat")
            else:
                if await self.uow.repo.get_active_chat_for_user(target_id):
                    raise ValueError("User is busy")

                chat = PrivateChat(
                    id=0,
                    user1_id=initiator_id,
                    user2_id=target_id,
                    is_active=True
                )

            user1 = await self.uow.user_repo.get_by_id(initiator_id)
            user2 = await self.uow.user_repo.get_by_id(target_id)

            if not user1 or not user2:
                raise ValueError("Users not found")

            if chat.id == 0:
                chat.id = await self.uow.repo.add(chat)
                await self.uow.commit()

            return mapping.chat_to_dto(
                chat,
                user_mapping.user_to_profile_dto(user1),
                user_mapping.user_to_profile_dto(user2)
            )
