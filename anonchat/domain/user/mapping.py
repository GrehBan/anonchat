from anonchat.domain.user.aggregate import User
from anonchat.domain.user.dto import UserProfileDTO, UserCreateDTO
from anonchat.domain.user.value_object import Interests, Reputation, Status, UserSettings
from anonchat.domain.user.enums import Gender


def user_to_profile_dto(user: User) -> UserProfileDTO:
    return UserProfileDTO(
        id=user.id,
        full_name=user.full_name,
        username=user.username,
        locale=user.locale,
        gender=user.gender,
        vip=user.status.vip,
        promotion=user.status.promotion,
        status=user.status.user_status,
        interests=user.interests.user_interests,
        reputation=user.reputation.score,
    )


def create_user_from_dto(dto: UserCreateDTO) -> User:
    return User(
        id=dto.id,
        username=dto.username,
        full_name=dto.full_name,
        locale=dto.locale,
        gender=Gender.ANY,
        status=Status(
            user_status=dto.status,
            promotion=dto.promotion,
            vip=False
        ),
        settings=UserSettings(search_gender=Gender.ANY),
        reputation=Reputation(),
        interests=Interests(),
    )
