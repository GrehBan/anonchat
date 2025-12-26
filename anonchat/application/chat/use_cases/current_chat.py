from typing import Protocol

from anonchat.domain.chat.uow import IChatUoW
from anonchat.domain.chat.dto import PrivateChatDTO
from anonchat.domain.chat import mapping
from anonchat.domain.user import mapping as user_mapping


class IGetCurrentChat(Protocol):
    uow: IChatUoW
    async def execute(self, user_id: int) -> PrivateChatDTO | None:
        ...


class GetCurrentChat(IGetCurrentChat):
    def __init__(self, uow: IChatUoW):
        self.uow = uow
    
    async def execute(self, user_id: int) -> PrivateChatDTO | None:
        async with self.uow:
            chat = await self.uow.repo.get_active_chat_for_user(user_id)
            
            if not chat:
                return None
            
            companion_id = chat.get_companion_id(user_id)
            
            user_me = await self.uow.user_repo.get_by_id(user_id)
            user_companion = await self.uow.user_repo.get_by_id(companion_id)
            
            if not user_me or not user_companion:
                return None 

            return mapping.chat_to_dto(
                chat,
                user1_dto=user_mapping.user_to_profile_dto(user_me if chat.user1_id == user_me.id else user_companion),
                user2_dto=user_mapping.user_to_profile_dto(user_companion if chat.user2_id == user_companion.id else user_me)
            )
