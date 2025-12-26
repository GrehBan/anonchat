from typing import Protocol

from anonchat.domain.base.repo import IRepo
from anonchat.domain.chat.aggregate import PrivateChat


class IChatRepo(IRepo, Protocol):
    async def add(self, chat: PrivateChat) -> int:
        ...
    
    async def get_by_id(self, chat_id: int) -> PrivateChat | None:
        ...
    
    async def get_chat_between(self, user_id_1: int, user_id_2: int) -> PrivateChat | None:
        ...
        
    async def get_active_chat_for_user(self, user_id: int) -> PrivateChat | None:
        ...
    
    async def delete_chat(self, chat_id: int) -> None:
        ...
