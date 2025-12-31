from sqlalchemy import select, delete, func, asc

from anonchat.domain.message.aggregate import Message
from anonchat.domain.message.repo import IMessageRepo
from anonchat.infrastructure.repositories.base.sqlalchemy import SqlalchemyRepo

from anonchat.infrastructure.database.models.message.message import MessageModel
from anonchat.infrastructure.database.models.message.mapping import (
    map_message_model_to_entity,
    map_message_entity_to_model
)

class SqlalchemyMessageRepo(SqlalchemyRepo, IMessageRepo):
    async def add(self, message: Message) -> Message:
        model = map_message_entity_to_model(message)

        self.session.add(model)
        await self.session.flush()
        
        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        stmt = select(MessageModel).where(MessageModel.message_id == message_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return map_message_model_to_entity(model)
        return None

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(asc(MessageModel.sequence))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [map_message_model_to_entity(m) for m in models]

    async def count_by_chat_id(self, chat_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(MessageModel)
            .where(MessageModel.chat_id == chat_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, message_id: int) -> None:
        stmt = delete(MessageModel).where(MessageModel.message_id == message_id)
        await self.session.execute(stmt)