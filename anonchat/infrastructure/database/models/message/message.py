from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey, DateTime, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from anonchat.infrastructure.database.models.base import Base


class MessageModel(Base):
    __tablename__ = "messages"
    
    __table_args__ = (
        Index('idx_chat_sequence', 'chat_id', 'sequence'),
        Index('idx_chat_active', 'chat_id', postgresql_where='deleted_at IS NULL'),
    )

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("private_chats.chat_id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    sequence: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    
    content_text: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    content_media: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
