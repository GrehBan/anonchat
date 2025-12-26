from anonchat.domain.base.dto import BaseDTO
from anonchat.domain.user.dto import UserProfileDTO
from anonchat.domain.message.dto import MessageDTO


class PrivateChatDTO(BaseDTO):
    id: int
    user1: UserProfileDTO
    user2: UserProfileDTO


class ChatCreateDTO(BaseDTO):
    user1: UserProfileDTO
    user2: UserProfileDTO


class StartChatRequestDTO(BaseDTO):
    user1_id: int
    user2_id: int


class ChatHistoryDTO(BaseDTO):
    chat_id: int
    messages: list[MessageDTO]
    total_count: int
