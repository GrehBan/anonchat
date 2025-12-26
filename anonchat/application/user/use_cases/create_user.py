from typing import Protocol

from anonchat.domain.user.uow import IUserUoW
from anonchat.domain.user.dto import UserCreateDTO, UserProfileDTO
from anonchat.domain.user import mapping


class ICreateUser(Protocol):
    uow: IUserUoW

    async def execute(self, dto: UserCreateDTO) -> UserProfileDTO:
        ...


class CreateUser(ICreateUser):
    def __init__(self, uow: IUserUoW):
        self.uow = uow
    
    async def execute(self, dto: UserCreateDTO) -> UserProfileDTO:
        async with self.uow:
            exists = await self.uow.repo.get_by_id(dto.id)
            if exists:
                return mapping.user_to_profile_dto(exists)
            
            new_user = mapping.create_user_from_dto(dto)

            await self.uow.repo.add(new_user)
            await self.uow.commit()
        
            return mapping.user_to_profile_dto(new_user)
