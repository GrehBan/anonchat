from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from anonchat.infrastructure.database.models.base import Base
from anonchat.infrastructure.database.models.user.user import UserModel


class PrivateChatModel(Base):
    __tablename__ = "private_chats"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    user1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    user2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user1: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[user1_id], lazy="selectin")
    user2: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[user2_id], lazy="selectin")


class MessageModel(Base):
    __tablename__ = "messages"

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("private_chats.chat_id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    content_text: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    
    content_media: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)