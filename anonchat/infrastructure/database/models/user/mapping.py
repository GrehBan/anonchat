from typing import Any

from anonchat.domain.user.aggregate import User
from anonchat.domain.user.value_object import Reputation, UserSettings, Status, Interests
from anonchat.domain.user.enums import Gender
from anonchat.infrastructure.database.models.user.user import (
    UserModel, UserSettingsModel, UserReputationModel, UserInterestModel
)


def map_user_entity_to_model(user: User) -> UserModel:
    return UserModel(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
        locale=user.locale,
        gender=user.gender,
        
        status_value=user.status.user_status,
        promotion=user.status.promotion,
        is_vip=user.status.vip,
        
        settings_relation=UserSettingsModel(
            user_id=user.id,
            search_gender=user.settings.search_gender,
            min_age=user.settings.min_age,
            max_age=user.settings.max_age
        ),
        
        reputation_relation=UserReputationModel(
            user_id=user.id,
            likes=user.reputation.likes,
            dislikes=user.reputation.dislikes
        ),
        
        interests_relation=[
            UserInterestModel(user_id=user.id, interest_id=interest_id)
            for interest_id in user.interests.user_interests
        ]
    )


def map_user_model_to_entity(model: UserModel) -> User:

    settings_data = model.settings_relation
    reputation_data = model.reputation_relation

    return User(
        id=model.user_id,
        full_name=model.full_name,
        username=model.username,
        locale=model.locale,
        gender=model.gender,
        
        settings=UserSettings(
            search_gender=settings_data.search_gender if settings_data else Gender.ANY,
            min_age=settings_data.min_age if settings_data else None,
            max_age=settings_data.max_age if settings_data else None
        ),
        
        reputation=Reputation(
            likes=reputation_data.likes if reputation_data else 0,
            dislikes=reputation_data.dislikes if reputation_data else 0
        ),
        
        status=Status(
            user_status=model.status_value,
            promotion=model.promotion,
            vip=model.is_vip
        ),
        
        interests=Interests(
            user_interests={i.interest_id for i in model.interests_relation}
        )
    )
