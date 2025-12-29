from typing import Protocol, TypeVar, Self

from anonchat.domain.base.lock import ILockFactory


class IUoW(Protocol):
    
    async def commit(self) -> None:
        ...
    
    async def rollback(self) -> None:
        ...

    async def __aenter__(self: Self) -> Self:
        ...

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        ...
    
    async def close(self) -> None:
        ...

class ILockUoW(IUoW, Protocol):
    lock: ILockFactory


UoWT = TypeVar("UoWT", bound="IUoW")
