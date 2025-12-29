from sqlalchemy.ext.asyncio import AsyncSession

from anonchat.domain.user.uow import IUserUoW
from anonchat.infrastructure.uow.base.sqlalchemy import BaseSqlalchemyUoW
from anonchat.infrastructure.repositories.user.sqlalchemy import SqlalchemyUserRepo


class SqlalchemyUserUoW(BaseSqlalchemyUoW, IUserUoW):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repo = SqlalchemyUserRepo(session)
