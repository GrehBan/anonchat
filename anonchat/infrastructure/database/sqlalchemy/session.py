from typing import Callable, Protocol
from functools import wraps
import inspect

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


class _SessionAccesable(Protocol):
    _session_maker: sessionmaker[AsyncSession]




class context_session:
    __mapping__ = {}

    @classmethod
    def wrap(cls, _session_accessable: type[_SessionAccesable]):
        cls.__mapping__[_session_accessable] = _session_accessable._session_maker

        return _session_accessable

    
    @classmethod
    def inject(cls):
        async def _deco(_session_accessable: type[_SessionAccesable]):
            async with cls.__mapping__[_session_accessable]() as session:
                def _wrap(func):
                    return func
                return _wrap
        return _deco


# Example


@context_session.wrap
class A:
    def __init__(self, session_maker: sessionmaker[AsyncSession]):
        self._session_maker = session_maker
    
    
    context_session.inject(A)
    def do(self, session):
        repo = Repo(session)
