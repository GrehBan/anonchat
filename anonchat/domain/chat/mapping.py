from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.domain.chat.dto import PrivateChatDTO
from anonchat.domain.user.dto import UserProfileDTO


def chat_to_dto(
    chat: PrivateChat, 
    user1_dto: UserProfileDTO, 
    user2_dto: UserProfileDTO
) -> PrivateChatDTO:
    return PrivateChatDTO(
        id=chat.id,
        user1=user1_dto,
        user2=user2_dto,
    )