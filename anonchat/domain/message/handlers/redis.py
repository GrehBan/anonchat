from anonchat.domain.base.handlers.redis import IDbEventHandler
from anonchat.domain.message.uow import IMessageUoW


class IMessageDbEventHandler(IDbEventHandler[IMessageUoW]):
    pass
