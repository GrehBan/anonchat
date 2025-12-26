from typing import Protocol, TypeVar


class IRepo(Protocol):
    pass

RepoT = TypeVar("RepoT", bound=IRepo)
