from typing import Protocol, Generic

from anonchat.domain.base.uow import UoWT


class IEventHandler(Protocol):
    async def handle(self, data: dict) -> None:
        ...


class IDbEventHandler(IEventHandler, Protocol[UoWT]):
    
    async def handle(self, data: dict, uow: UoWT) -> None:
        ...
