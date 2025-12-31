from sqlalchemy import select, delete, func, asc, text
from datetime import datetime, timezone

from anonchat.domain.message.aggregate import Message
from anonchat.domain.message.repo import IMessageRepo
from anonchat.infrastructure.repositories.base.sqlalchemy import SqlalchemyRepo

from anonchat.infrastructure.database.models.message.message import MessageModel
from anonchat.infrastructure.database.models.message.mapping import (
    map_message_model_to_entity,
    map_message_entity_to_model
)
from anonchat.domain.message.value_object import MessageContent, MessageText, MediaAttachment
from anonchat.domain.message.mapping import content_to_message_content_entity

class SqlalchemyMessageRepo(SqlalchemyRepo, IMessageRepo):

    async def add(self, message: Message) -> Message:
        model = map_message_entity_to_model(message)
        self.session.add(model)
        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        stmt = select(MessageModel).where(MessageModel.message_id == message_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return map_message_model_to_entity(model)
        return None

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        stmt = text("""
            SELECT 
                message_id,
                chat_id,
                sender_id,
                virtual_sequence,
                content_text,
                content_media,
                created_at,
                deleted_at
            FROM messages_ordered
            WHERE chat_id = :chat_id 
              AND deleted_at IS NULL
            ORDER BY virtual_sequence ASC
            LIMIT :limit OFFSET :offset
        """)
        
        result = await self.session.execute(
            stmt,
            {"chat_id": chat_id, "limit": limit, "offset": offset}
        )
        
        rows = result.mappings().all()
        
        messages = []
        for row in rows:
            message = Message(
                id=row["message_id"],
                chat_id=row["chat_id"],
                sender_id=row["sender_id"],
                sequence=row["virtual_sequence"],
                content=content_to_message_content_entity(row["content_text"], row["content_media"]),
                created_at=row["created_at"],
                deleted_at=row.get("deleted_at")
            )
            messages.append(message)
        
        return messages

    async def count_by_chat_id(self, chat_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .where(MessageModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, message_id: int) -> None:
        stmt = (
            select(MessageModel)
            .where(MessageModel.message_id == message_id)
            .where(MessageModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            model.deleted_at = datetime.now(timezone.utc)
