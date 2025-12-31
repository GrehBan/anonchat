from anonchat.domain.base.handlers.redis import IDbEventHandler
from anonchat.domain.chat.uow import IChatUoW


class IChatDbEventHandler(IDbEventHandler[IChatUoW]):
    pass
