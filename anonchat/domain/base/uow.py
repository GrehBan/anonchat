from typing import Protocol, TypeVar, Self

from anonchat.domain.base.repo import RepoT


class IUoW(Protocol):
    repo: RepoT
    
    async def commit(self) -> None:
        ...
    
    async def rollback(self) -> None:
        ...

    async def __aenter__(self: Self) -> Self:
        ...

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        ...

UoWT = TypeVar("UoWT", bound="IUoW")
