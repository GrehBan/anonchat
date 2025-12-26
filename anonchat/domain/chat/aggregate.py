from dataclasses import dataclass, field
from datetime import datetime

from anonchat.domain.base.aggregate import IAggregateRoot
from anonchat.domain.user.aggregate import User


@dataclass(eq=False)
class PrivateChat(IAggregateRoot):
    id: int
    user1: User
    user2: User
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_companion_id(self, my_id: int) -> int:
        if self.user1.id == my_id:
            return self.user2.id
        return self.user1.id

    def close_chat(self) -> None:
        self.is_active = False
