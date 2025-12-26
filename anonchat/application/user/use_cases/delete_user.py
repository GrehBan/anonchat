from typing import Protocol
from anonchat.domain.user.uow import IUserUoW


class IDeleteUser(Protocol):
    uow: IUserUoW

    async def execute(self, user_id: int) -> None:
        ...


class DeleteUser(IDeleteUser):
    def __init__(self, uow: IUserUoW):
        self.uow = uow
    
    async def execute(self, user_id: int) -> None:
        async with self.uow:
            existing_user = await self.uow.repo.get_by_id(user_id)
            if not existing_user:
                raise ValueError(f"User with id {user_id} not found")

            await self.uow.repo.delete_by_id(user_id)
            
            await self.uow.commit()
