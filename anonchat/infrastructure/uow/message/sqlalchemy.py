from sqlalchemy.ext.asyncio import AsyncSession

from anonchat.domain.message.uow import IMessageUoW
from anonchat.infrastructure.uow.base.sqlalchemy import BaseSqlalchemyUoW
from anonchat.infrastructure.repositories.message.sqlalchemy import SqlalchemyMessageRepo


class SqlalchemyMessageUoW(BaseSqlalchemyUoW, IMessageUoW):
    def __init__(self, session: AsyncSession, auto_commit: bool = False) -> None:
        super().__init__(session, auto_commit)
        self.repo = SqlalchemyMessageRepo(session)
