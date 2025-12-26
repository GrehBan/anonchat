from dataclasses import dataclass, field
from datetime import datetime

from anonchat.domain.base.aggregate import IAggregateRoot


@dataclass(eq=False)
class PrivateChat(IAggregateRoot):
    id: int
    user1_id: int
    user2_id: int
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_companion_id(self, my_id: int) -> int:
        if self.user1_id == my_id:
            return self.user2_id
        return self.user1_id

    def close_chat(self) -> None:
        self.is_active = False