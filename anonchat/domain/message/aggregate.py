from dataclasses import dataclass, field
from datetime import datetime, timezone

from anonchat.domain.base.aggregate import IAggregateRoot
from anonchat.domain.message.value_object import MessageContent, MediaAttachment


@dataclass(eq=False)
class Message(IAggregateRoot):
    id: int
    chat_id: int
    sender_id: int
    content: MessageContent
    sequence: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = None

    def edit_text(self, new_text: str) -> None:
        if not self.content.text:
            raise ValueError("Cannot edit text of a message without text")
        self.content = self.content.with_text(new_text)
    
    def attach_media(self, *media: MediaAttachment) -> None:
        self.content = self.content.attach_media(*media)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        if not self.is_deleted:
            self.deleted_at = datetime.now(timezone.utc)
