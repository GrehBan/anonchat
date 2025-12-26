from typing import Protocol

from anonchat.domain.user.uow import IUserUoW
from anonchat.domain.user.dto import UserProfileDTO
from anonchat.domain.user import mapping
from anonchat.domain.user.exceptions import UserNotFoundException


class IGetUser(Protocol):
    uow: IUserUoW

    async def execute(self, user_id: int) -> UserProfileDTO:
        ...


class GetUser(IGetUser):
    def __init__(self, uow: IUserUoW):
        self.uow = uow
    
    async def execute(self, user_id: int) -> UserProfileDTO:
        async with self.uow:
            user = await self.uow.repo.get_by_id(user_id)
            
            if not user:
                raise UserNotFoundException(f"User with id {user_id} not found")
            
            return mapping.user_to_profile_dto(user)