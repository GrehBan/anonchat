from datetime import datetime, timezone

from sqlalchemy import BigInteger, ForeignKey, Boolean, DateTime
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user1: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[user1_id])
    user2: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[user2_id])