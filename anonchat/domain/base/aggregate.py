from typing import Protocol

from anonchat.domain.base.entity import BaseEntity


class IAggregateRoot(BaseEntity, Protocol):
    ...
