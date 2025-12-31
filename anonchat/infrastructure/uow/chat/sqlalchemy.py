from sqlalchemy.ext.asyncio import AsyncSession

from anonchat.domain.chat.uow import IChatUoW
from anonchat.infrastructure.uow.base.sqlalchemy import BaseSqlalchemyUoW
from anonchat.infrastructure.repositories.chat.sqlalchemy import SqlalchemyChatRepo
from anonchat.infrastructure.repositories.user.sqlalchemy import SqlalchemyUserRepo
from anonchat.infrastructure.repositories.message.sqlalchemy import SqlalchemyMessageRepo


class SqlalchemyChatUoW(BaseSqlalchemyUoW, IChatUoW):
    def __init__(self, session: AsyncSession, auto_commit: bool = False) -> None:
        super().__init__(session, auto_commit)
        self.repo = SqlalchemyChatRepo(session)
        self.user_repo = SqlalchemyUserRepo(session)
        self.message_repo = SqlalchemyMessageRepo(session)
