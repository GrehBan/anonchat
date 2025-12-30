from dataclasses import dataclass

from anonchat.domain.base.aggregate import IAggregateRoot
from anonchat.domain.user.enums import Gender, Locale, UserReputation, ReputationChange, UserPromotion
from anonchat.domain.user.value_object import UserSettings, Reputation, Interests, Status


@dataclass(eq=False)
class User(IAggregateRoot):
    id: int
    full_name: str
    gender: Gender
    settings: UserSettings
    reputation: Reputation
    status: Status
    interests: Interests
    locale: Locale
    username: str | None = None

    @property
    def is_banned(self) -> bool:
        return self.status.is_banned
    
    @property
    def is_admin(self) -> bool:
        return self.status.is_admin
    
    @property
    def is_owner(self) -> bool:
        return self.status.is_owner

    def add_interests(self, *interests: int) -> None:
        self.interests = self.interests.add_interests(*interests)
    
    def interested_in(self, *interests: int, strict: bool = True) -> bool:
        return self.interests.matches(
            *interests,
            strict=strict
        )
    
    def recieve_feedback(self, reputation: UserReputation, change: ReputationChange, value: int) -> None:
        self.reputation = self.reputation.update(
            reputation=reputation,
            change=change,
            value=value
        )
    
    def ban(self):
        self.status = self.status.ban()
    
    def promote(self, promotion: UserPromotion):
        self.status = self.status.promote(promotion)
    
    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
