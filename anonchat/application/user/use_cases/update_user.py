from typing import Protocol

from anonchat.domain.user.uow import IUserUoW
from anonchat.domain.user.dto import UserProfileDTO
from anonchat.domain.user.aggregate import User
from anonchat.domain.user import mapping
from anonchat.domain.user.exceptions import UserNotFoundException


class IUpdateUser(Protocol):
    uow: IUserUoW

    async def execute(self, user: User) -> UserProfileDTO:
        ...


class UpdateUser(IUpdateUser):
    def __init__(self, uow: IUserUoW):
        self.uow = uow
    
    async def execute(self, user: User) -> UserProfileDTO:
        async with self.uow:
            user = await self.uow.repo.get_by_id(user.id)
            
            if not user:
                raise UserNotFoundException(f"User with id {user.id} not found")
            
            await self.uow.repo.update(user)
            await self.uow.commit()
            
            return mapping.user_to_profile_dto(user)
