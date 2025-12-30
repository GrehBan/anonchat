from typing import Protocol

from anonchat.domain.chat.uow import ILockChatUoW
from anonchat.domain.chat.dto import StartChatRequestDTO, PrivateChatDTO
from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.domain.chat import mapping
from anonchat.domain.user import mapping as user_mapping
from anonchat.domain.base.exceptions import DomainException
from anonchat.domain.user.exceptions import UserAlreadyInChatException, UserIsBusyException, UserNotFoundException, UserIsSelfException
from anonchat.infrastructure.cache import key_gen


class IStartChat(Protocol):
    uow: ILockChatUoW
    async def execute(self, initiator_id: int, dto: StartChatRequestDTO) -> PrivateChatDTO:
        ...


class StartChat(IStartChat):
    def __init__(self, uow: ILockChatUoW):
        self.uow = uow
    
    async def execute(self, initiator_id: int, dto: StartChatRequestDTO) -> PrivateChatDTO:
        target_id = dto.user2_id
        
        if initiator_id == target_id:
            raise UserIsSelfException("Cannot start chat with yourself")

        first_lock_id, second_lock_id = sorted((initiator_id, target_id))
        first_key = key_gen.lock_user(user_id=first_lock_id)
        second_key = key_gen.lock_user(user_id=second_lock_id)

        try:
            async with self.uow.lock(first_key):
                async with self.uow.lock(second_key):
                    async with self.uow:
                        initiator_chat = await self.uow.repo.get_active_chat_for_user(initiator_id)
                        if initiator_chat:
                            raise UserAlreadyInChatException("You already have an active chat")
                        
                        target_chat = await self.uow.repo.get_active_chat_for_user(target_id)
                        if target_chat:
                            raise UserIsBusyException("Target user is busy")

                        user1 = await self.uow.user_repo.get_by_id(initiator_id)
                        user2 = await self.uow.user_repo.get_by_id(target_id)

                        if not user1 or not user2:
                            raise UserNotFoundException("Users not found")
                        
                        chat = PrivateChat(
                            id=0,
                            user1_id=user1.id,
                            user2_id=user2.id
                        )

                        chat = await self.uow.repo.add(chat)
                        await self.uow.commit()
                        
                        return mapping.chat_to_dto(
                            chat,
                            user_mapping.user_to_profile_dto(user1),
                            user_mapping.user_to_profile_dto(user2)
                        )
        except DomainException:
            raise
        except ValueError as e:
            raise ValueError("System is busy, please try again") from e
