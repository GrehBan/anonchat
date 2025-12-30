from pydantic import Field

from anonchat.domain.base.dto import BaseDTO
from anonchat.domain.user.enums import Locale, Gender, UserPromotion, UserStatus


class UserBaseDTO(BaseDTO):
    id: int
    full_name: str
    username: str | None = None
    locale: Locale = Locale.UNSET
    status: UserStatus = UserStatus.ACTIVE
    promotion: UserPromotion = UserPromotion.USER


class UserCreateDTO(UserBaseDTO):
    pass


class UserProfileDTO(UserBaseDTO):
    gender: Gender
    reputation: int
    interests: set[int] = Field(default_factory=set)
    vip: bool = False


class SearchParamsDTO(BaseDTO):
    user_id: int
    my_gender: Gender
    search_gender: Gender
    interests: set[int] = Field(default_factory=set)
