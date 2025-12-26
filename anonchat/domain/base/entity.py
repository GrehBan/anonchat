from typing import Protocol, TypeVar, Generic
from abc import ABC

ET = TypeVar("ET", bound="IEntity")


class IEntity(Protocol):
    id: int


class BaseEntity(IEntity, ABC):
    def __eq__(self: ET, other: ET) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
