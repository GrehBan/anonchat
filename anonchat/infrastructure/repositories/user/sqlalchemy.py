from sqlalchemy import select, delete

from anonchat.domain.user.repo import IUserRepo
from anonchat.domain.user.aggregate import User
from anonchat.infrastructure.repositories.base.sqlalchemy import SqlalchemyRepo

from anonchat.infrastructure.database.models.user.user import UserModel
from anonchat.infrastructure.database.models.user.mapping import (
    map_user_model_to_entity,
    map_user_entity_to_model
)


class SqlalchemyUserRepo(SqlalchemyRepo, IUserRepo):
    
    async def get_by_id(self, id: int) -> User | None:
        stmt = (
            select(UserModel)
            .where(UserModel.user_id == id)
        )
        
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
            
        return map_user_model_to_entity(model)

    async def add(self, user: User) -> User:
        user_model = map_user_entity_to_model(user)
        self.session.add(user_model)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        user_model = map_user_entity_to_model(user)
        await self.session.merge(user_model)
        await self.session.flush()
        return user

    async def delete_by_id(self, id: int) -> None:
        stmt = delete(UserModel).where(UserModel.user_id == id)
        await self.session.execute(stmt)

        await self.session.flush()
