from typing import Protocol

from anonchat.domain.base.uow import UoWT


class IWokrker(Protocol):

    def stop(self) -> None:
        ...

    async def consume(self) -> None:
        ...
