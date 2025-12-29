from typing import Protocol

from anonchat.domain.base.uow import IUoW, ILockUoW
from anonchat.domain.message.repo import IMessageRepo 


class IMessageUoW(IUoW, Protocol):
    repo: IMessageRepo


class ILockMessageUoW(IMessageUoW, ILockUoW, Protocol):
    pass
