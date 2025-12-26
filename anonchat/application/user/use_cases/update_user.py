from typing import Protocol

from anonchat.domain.user.uow import IUserUoW
from anonchat.domain.user.dto import UserUpdateDTO, UserProfileDTO
from anonchat.domain.user import mapping
from anonchat.domain.user.exceptions import UserNotFoundException


class IUpdateUser(Protocol):
    uow: IUserUoW

    async def execute(self, dto: UserUpdateDTO) -> UserProfileDTO:
        ...


class UpdateUser(IUpdateUser):
    def __init__(self, uow: IUserUoW):
        self.uow = uow
    
    async def execute(self, dto: UserUpdateDTO) -> UserProfileDTO:
        async with self.uow:
            user = await self.uow.repo.get_by_id(dto.id)
            
            if not user:
                raise UserNotFoundException(f"User with id {dto.id} not found")
            
            mapping.update_user_from_dto(dto, user)

            await self.uow.commit()
            
            return mapping.user_to_profile_dto(user)
