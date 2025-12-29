from sqlalchemy.ext.asyncio import AsyncSession

from anonchat.infrastructure.uow.base.sqlalchemy import BaseSqlalchemyUoW
from anonchat.infrastructure.uow.user.sqlalchemy import SqlalchemyUserUoW
from anonchat.infrastructure.uow.chat.sqlalchemy import SqlalchemyChatUoW
from anonchat.infrastructure.uow.message.sqlalchemy import SqlalchemyMessageUoW


class SqlalchemyUoW(BaseSqlalchemyUoW):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

        self.chat = SqlalchemyChatUoW(session)
        self.user = SqlalchemyUserUoW(session)
        self.message = SqlalchemyMessageUoW(session)
