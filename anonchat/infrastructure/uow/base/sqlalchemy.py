from sqlalchemy.ext.asyncio import AsyncSession

from anonchat.domain.base.uow import IUoW


class BaseSqlalchemyUoW(IUoW):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    @property
    def session(self) -> AsyncSession:
        return self._session
    
    async def commit(self) -> None:
        await self.session.commit()
    
    async def rollback(self) -> None:
        await self.session.rollback()
    
    async def __aenter__(self) -> "BaseSqlalchemyUoW":
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
    
    async def close(self):
        await self.session.close()
