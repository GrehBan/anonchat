from typing import Protocol

from anonchat.domain.base.uow import IUoW
from anonchat.domain.user.repo import IUserRepo


class IUserUoW(IUoW, Protocol):
    repo: IUserRepo
