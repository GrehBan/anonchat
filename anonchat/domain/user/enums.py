from enum import StrEnum, IntEnum, unique, auto

from anonchat.domain.base.enums import UpperStrEnum


@unique
class Locale(StrEnum):
    EN = "en"
    RU = "ru"
    UNSET = "UNSET"


@unique
class Gender(UpperStrEnum):
    MALE = auto()
    FEMALE = auto()
    ANY = auto()


@unique
class UserStatus(UpperStrEnum):
    BANNED = auto()
    ACTIVE = auto()
    DELETED = auto()


@unique
class UserPromotion(UpperStrEnum):
    USER = auto()
    ADMIN = auto()
    OWNER = auto()


@unique
class UserReputation(UpperStrEnum):
    LIKE = auto()
    DISLIKE = auto()


@unique
class ReputationChange(IntEnum):
    INCREASE = 1
    DECREASE = -1