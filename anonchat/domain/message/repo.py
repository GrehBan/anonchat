from typing import Protocol

from anonchat.domain.base.repo import IRepo
from anonchat.domain.message.aggregate import Message


class IMessageRepo(IRepo, Protocol):
    async def add(self, message: Message) -> int:
        ...
    
    async def get_by_id(self, message_id: int) -> Message | None:
        ...

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        ...

    async def count_by_chat_id(self, chat_id: int) -> int:
        ...

    async def delete(self, message_id: int) -> None:
        ...