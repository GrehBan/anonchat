from dataclasses import dataclass, field

from anonchat.domain.base.value_object import IValueObject
from anonchat.domain.user.enums import Gender, UserStatus, UserPromotion, UserReputation, ReputationChange


@dataclass(frozen=True)
class UserSettings(IValueObject["UserSettings"]):
    search_gender: Gender = Gender.ANY
    min_age: int | None = None
    max_age: int | None = None

    def __post_init__(self) -> None:
        if (
            self.min_age is not None
            and self.max_age is not None
            and self.min_age > self.max_age
        ):
            raise ValueError("Min age cannot be greater than max age")


@dataclass(frozen=True)
class Reputation(IValueObject["Reputation"]):
    likes: int = 0
    dislikes: int = 0

    @property
    def score(self) -> int:
        return self.likes - self.dislikes
    
    def update(self, reputation: UserReputation, change: ReputationChange, value: int) -> Reputation:
        if value < 0:
            raise ValueError("Reputation value must be non-negative")

        sign = 1 if change == ReputationChange.INCREASE else -1
        delta = value * sign

        if reputation == UserReputation.LIKE:
            return self.increase_likes(delta)
        return self.increase_dislikes(delta)

    def increase_dislikes(self, value: int) -> Reputation:
        return Reputation(
            likes=self.likes,
            dislikes=max(0, self.dislikes + value)
        )

    
    def increase_likes(self, value: int) -> Reputation:
        return Reputation(
            likes=max(0, self.likes + value),
            dislikes=self.dislikes
        )


@dataclass(frozen=True)
class Status(IValueObject["Status"]):
    user_status: UserStatus
    promotion: UserPromotion
    vip: bool = False
    
    @property
    def is_banned(self) -> bool:
        return self.user_status == UserStatus.BANNED
    
    @property
    def is_admin(self) -> bool:
        return self.promotion in (UserPromotion.ADMIN, UserPromotion.OWNER)
    
    @property
    def is_owner(self) -> bool:
        return self.promotion == UserPromotion.OWNER
    
    def ban(self) -> Status:
        return Status(
            user_status=UserStatus.BANNED,
            promotion=self.promotion
        )
    
    def promote(self, promotion: UserPromotion) -> Status:
        return Status(
            user_status=self.user_status,
            promotion=promotion
        )


@dataclass(frozen=True)
class Interests(IValueObject["Interests"]):
    user_interests: set[int] = field(default_factory=set)

    def add_interests(self, *interests: int) -> "Interests":
        if not interests:
            return self
        
        new_interests = self.user_interests | set(interests)
        return Interests(user_interests=new_interests)

    def remove_interests(self, *interests: int) -> "Interests":
        if not interests:
            return self
        
        new_interests = self.user_interests - set(interests)
        return Interests(user_interests=new_interests)

    def matches(self, *interests: int, strict: bool = True) -> bool:
        if not interests:
            return True

        if strict:
            return self.user_interests.issuperset(interests)
        
        return not self.user_interests.isdisjoint(interests)

    def __contains__(self, interest: int) -> bool:
        return interest in self.user_interests