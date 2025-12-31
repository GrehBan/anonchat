from typing import TypedDict, List

from anonchat.domain.user.aggregate import User
from anonchat.domain.user.value_object import UserSettings, Reputation, Status, Interests


class RedisUserSettings(TypedDict):
    search_gender: str
    min_age: int
    max_age: int


class RedisUserReputation(TypedDict):
    likes: int
    dislikes: int


class RedisUserStatus(TypedDict):
    val: str
    promo: str
    vip: bool


class RedisUserData(TypedDict):
    id: int
    full_name: str
    username: str
    locale: str
    gender: str
    settings: RedisUserSettings
    reputation: RedisUserReputation
    status: RedisUserStatus
    interests: List[str]


def map_user_entity_to_redis_data(user: User) -> RedisUserData:
    data: RedisUserData = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "locale": user.locale,
        "gender": user.gender,
        "settings": {
            "search_gender": user.settings.search_gender,
            "min_age": user.settings.min_age,
            "max_age": user.settings.max_age,
        },
        "reputation": {
            "likes": user.reputation.likes,
            "dislikes": user.reputation.dislikes,
        },
        "status": {
            "val": user.status.user_status,
            "promo": user.status.promotion,
            "vip": user.status.vip,
        },
        "interests": list(user.interests.user_interests),
    }

    return data


def map_redis_data_to_user_entity(data: RedisUserData) -> User:
    return User(
        id=data["id"],
        full_name=data["full_name"],
        username=data["username"],
        locale=data["locale"],
        gender=data["gender"],
        settings=UserSettings(
            search_gender=data["settings"]["search_gender"],
            min_age=data["settings"]["min_age"],
            max_age=data["settings"]["max_age"]
        ),
        reputation=Reputation(
            likes=data["reputation"]["likes"],
            dislikes=data["reputation"]["dislikes"]
        ),
        status=Status(
            user_status=data["status"]["val"],
            promotion=data["status"]["promo"],
            vip=data["status"]["vip"]
        ),
        interests=Interests(set(data["interests"]))
    )