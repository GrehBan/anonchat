from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.domain.chat.dto import PrivateChatDTO

from anonchat.domain.user.mapping import user_to_profile_dto


def chat_to_dto(chat: PrivateChat) -> PrivateChatDTO:
    return PrivateChatDTO(
        id=chat.id,
        user1=user_to_profile_dto(chat.user1),
        user2=user_to_profile_dto(chat.user2),
    )
