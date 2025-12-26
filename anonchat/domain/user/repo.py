from typing import Protocol

from anonchat.domain.base.repo import IRepo
from anonchat.domain.user.aggregate import User


class IUserRepo(IRepo, Protocol):
    async def add(self, user: User) -> User:
        ...
    
    async def get_by_id(self, id: int) -> User | None:
        ...
    
    async def delete_by_id(self, id: int) -> None:
        ...
