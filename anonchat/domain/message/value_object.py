from dataclasses import dataclass, field

from anonchat.domain.base.value_object import IValueObject


@dataclass(frozen=True)
class MessageText(IValueObject["MessageText"]):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Message text cannot be empty or whitespace only")
        
        if len(self.value) > 4096:
            raise ValueError("Message text exceeds maximum length of 4096 characters")


@dataclass(frozen=True)
class MediaAttachment(IValueObject["MediaAttachment"]):
    file_id: str
    
    def __post_init__(self) -> None:
        if not self.file_id:
            raise ValueError("Media file_id cannot be empty")


@dataclass(frozen=True)
class MessageContent(IValueObject["MessageContent"]):
    text: MessageText | None = None
    media: tuple[MediaAttachment, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.text is None and not self.media:
            raise ValueError("Message content must contain at least text or media")

    @property
    def has_media(self) -> bool:
        return len(self.media) > 0

    @property
    def raw_text(self) -> str:
        return self.text.value if self.text else ""

    def with_text(self, text: str) -> "MessageContent":
        return MessageContent(
            text=MessageText(text),
            media=self.media
        )
    
    def attach_media(self, *media: MediaAttachment) -> "MessageContent":
        return MessageContent(
            text=self.text,
            media=self.media + media
        )
