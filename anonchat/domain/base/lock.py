from typing import Protocol, AsyncContextManager

class ILock(AsyncContextManager, Protocol):
    pass


class ILockFactory(Protocol):
    """Абстракция фабрики, которая создает блокировки"""
    def lock(self, key: str, ttl_ms: int = 5000) -> ILock:
        ...
    
    def __call__(self, key: str, ttl_ms: int = 5000) -> ILock:
        ...
