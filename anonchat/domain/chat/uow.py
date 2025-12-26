from typing import Protocol

from anonchat.domain.base.uow import IUoW
from anonchat.domain.chat.repo import IChatRepo
from anonchat.domain.user.repo import IUserRepo 
from anonchat.domain.message.repo import IMessageRepo 


class IChatUoW(IUoW, Protocol):
    repo: IChatRepo
    user_repo: IUserRepo
    message_repo: IMessageRepo