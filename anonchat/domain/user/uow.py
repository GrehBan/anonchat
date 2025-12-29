from typing import Protocol

from anonchat.domain.base.uow import IUoW, ILockUoW
from anonchat.domain.user.repo import IUserRepo


class IUserUoW(IUoW, Protocol):
    repo: IUserRepo


class ILockUserUoW(IUserUoW, ILockUoW, Protocol):
    pass
