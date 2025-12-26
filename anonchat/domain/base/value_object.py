from typing import Protocol, TypeVar

VOT = TypeVar("VOT", bound="IValueObject")


class IValueObject(Protocol[VOT]):
    def __eq__(self: VOT, other: VOT) -> bool:
        ...
    
    def __hash__(self) -> int:
        ...
