from anonchat.domain.base.handlers.redis import IDbEventHandler
from anonchat.domain.user.uow import IUserUoW


class IUserDbEventHandler(IDbEventHandler[IUserUoW]):
    pass
