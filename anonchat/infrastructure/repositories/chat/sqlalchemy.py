from sqlalchemy import select, delete, or_, and_

from anonchat.domain.chat.aggregate import PrivateChat
from anonchat.domain.chat.repo import IChatRepo
from anonchat.infrastructure.repositories.base.sqlalchemy import SqlalchemyRepo

from anonchat.infrastructure.database.models.chat.chat import PrivateChatModel
from anonchat.infrastructure.database.models.chat.mapping import (
    map_chat_model_to_entity,
    map_chat_entity_to_model
)


class SqlalchemyChatRepo(SqlalchemyRepo, IChatRepo):

    async def add(self, chat: PrivateChat) -> PrivateChat:
        model = map_chat_entity_to_model(chat)

        self.session.add(model)
        await self.session.flush()
        
        return chat

    async def update(self, chat: PrivateChat) -> PrivateChat:
        model = map_chat_entity_to_model(chat)

        await self.session.merge(model)
        await self.session.flush()
        
        return chat

    async def get_by_id(self, chat_id: int) -> PrivateChat | None:
        stmt = select(PrivateChatModel).where(PrivateChatModel.chat_id == chat_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
            
        return map_chat_model_to_entity(model)

    async def get_chat_between(self, user_id_1: int, user_id_2: int) -> PrivateChat | None:
        stmt = select(PrivateChatModel).where(
            or_(
                and_(PrivateChatModel.user1_id == user_id_1, PrivateChatModel.user2_id == user_id_2),
                and_(PrivateChatModel.user1_id == user_id_2, PrivateChatModel.user2_id == user_id_1)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return map_chat_model_to_entity(model)
        return None

    async def get_active_chat_for_user(self, user_id: int) -> PrivateChat | None:
        stmt = select(PrivateChatModel).where(
            or_(
                PrivateChatModel.user1_id == user_id,
                PrivateChatModel.user2_id == user_id
            )
        ).where(
            PrivateChatModel.is_active == True
        )
        
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return map_chat_model_to_entity(model)
        return None

    async def delete_chat(self, chat_id: int) -> None:
        stmt = delete(PrivateChatModel).where(PrivateChatModel.chat_id == chat_id)
        await self.session.execute(stmt)
        await self.session.flush()