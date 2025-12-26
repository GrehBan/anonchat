from anonchat.domain.user.aggregate import User
from anonchat.domain.user.dto import UserProfileDTO, UserCreateDTO, UserUpdateDTO
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


def update_user_from_dto(dto: UserUpdateDTO, user: User) -> User:
    data = dto.model_dump(exclude_unset=True, exclude_defaults=True, exclude={"id"})
    
    if not data:
        return user

    updates = {}

    if any(k in data for k in ("status", "promotion", "vip")):
        updates["status"] = Status(
            user_status=data.get("status", user.status.user_status),
            promotion=data.get("promotion", user.status.promotion),
            vip=data.get("vip", user.status.vip),
        )

    if "interests" in data:
        updates["interests"] = Interests(user_interests=data["interests"])

    for field in ("full_name", "username", "gender", "locale", "settings"):
        if field in data:
            updates[field] = data[field]

    if updates:
        user.update(**updates)
    
    return user