from datetime import datetime
from pydantic import Field

from anonchat.domain.base.dto import BaseDTO


class MessageDTO(BaseDTO):
    id: int
    chat_id: int
    sender_id: int
    text: str
    created_at: datetime
    media: list[str] = Field(default_factory=list)


class SendMessageDTO(BaseDTO):
    text: str = Field(min_length=1, max_length=4096)
    media: list[str] = Field(default_factory=list)

