from typing import Protocol

from anonchat.domain.base.uow import IUoW
from anonchat.domain.message.repo import IMessageRepo 


class IMessageUoW(IUoW, Protocol):
    repo: IMessageRepo
