from sqlalchemy.ext.asyncio import AsyncSession

from anonchat.domain.base.repo import IRepo


class SqlalchemyRepo(IRepo):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    @property
    def session(self) -> AsyncSession:
        return self._session
